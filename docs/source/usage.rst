Usage
=====

A very simple example is shown below. It is broken into three parts:

* definition
* invocation (calling)
* execution (receiving)

Note however that this is (nearly) a single codebase; though you are deploying to two places (some application and a cloud function to dispatch to) the deployable artifacts only differ in ``main.py``, if at all.


Definition
----------

Defining a dispatchable function looks like this:

.. literalinclude:: ../../sample/functions.py
    :pyobject: my_func

Note that ``my_func`` is just a normal Python function that takes arguments. Arguments can be anything that ``pickle`` knows how to serialize, which covers all primitives, dataclasses, and many other structures, but does *not* include generators or callables (among other things). The only thing you need to do to any Python function to cause it to dispatch is to apply the ``@dispatch`` decorator.


Invocation
----------

Once your function is defined in your application, you call it just like any other function:

.. literalinclude:: ../../sample/my_module.py
    :pyobject: call_dispatched_function

When you execute this code by calling ``my_module.call_dispatched_function()``, your cloud function will be invoked and the specified function will be executed remotely.

**Note:** for obvious reasons, the dispatched execution won't work until the cloud function is properly deployed as specified below.


Execution
---------

Your cloud function will need an entry point. You should use the provided ``execute`` method:

.. literalinclude:: ../../sample/main.py

**Note:** the ``main.py`` file deployed with the executor may or may not be the same as that deployed with the invoker; this is really dependent on whether your main application **also** deploys as a cloud function or as something else.

Your codebase can then be deployed to Cloud Functions with the entrypoint specified:

.. code-block:: sh

    $ gcloud functions deploy ${FUNCTION_NAME} --trigger-topic=${TOPIC_NAME} --source=${SOURCE_DIR} --entry-point=execute_dispatched ...


Output
------

Once your function is deployed, you can call it and you will see something like the following in your logs:

::

    I 2020-03-13T22:24:35.427Z my-topic 1043501608491014 pushing function call to pubsub: functions.my_func

... followed shortly by something like this in your cloud function logs, showing execution of the function:

::

    D 2020-03-13T22:24:35.436Z my-topic 1043501608491013 Function execution started
    I 2020-03-13T22:24:35.526Z my-topic 1043501608491013 received event 1043501608491013 sent at 2020-03-13T22:24:35.095Z
    I 2020-03-13T22:24:35.526Z my-topic 1043501608491013 executing: functions.my_func
    I 2020-03-13T22:24:35.526Z my-topic 1043501608491013 a is just right: hooray!
    D 2020-03-13T22:24:35.527Z my-topic 1043501608491013 Function execution took 92 ms, finished with status: 'ok'


Deployable Example
------------------

A complete, working sample can be found in the ``./sample`` directory. To see it in action:

* Enable Cloud Functions and PubSub in GCP (see Google documentation for this)
* Create a pubsub topic in GCP (the command below assumes it's ``my-topic``)
* Pick an unused name for your function (the command below assumes it's ``my-func``)

Then run the following command:

::

    $ gcloud functions deploy my-func --trigger-topic=my-topic --source=sample --entry-point=execute_dispatched --runtime=python37 --memory=128MB --max-instances=1 --set-env-vars CLOUD_FUNCTIONS_DISPATCH_GCP_PUBSUB_TOPIC=my-topic

Now set `GCP_PROJECT` and `CLOUD_FUNCTIONS_DISPATCH_GCP_PUBSUB_TOPIC` locally and:

::

    $ cd sample
    $ PYTHONPATH=..:$PYTHONPATH python -c "import functions; functions.echo(1, 'a', x=7); functions.my_func(1, 2)"

After a few seconds you will see the output of your cloud function showing the arguments passed in your cloud logging tools.
