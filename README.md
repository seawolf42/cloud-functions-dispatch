# Cloud Functions Dispatch

Cloud Functions Dispatch gives you the ability to dispatch in-process no-response function calls to a remote cloud function by simply applying a decorator to your function.

This is useful for tasks such as the following:

* update a database record separately from this process
* fan-out of a large job into chunks that are completed independently
* run secondary processes as side-effects of receiving a request

Basically any task that requires parameters but not process state and does not need to return a value is a great candidate for dispatching.

**SECURITY NOTE:** Note that improper configuration of the messaging system (only Google's PubSub at the moment) may allow an attacker to run arbitrary code within your cloud function. See [security](#security) below.


## Prerequisites and Notes

The following should be considered when using this library:

The library assumes all method calls are from a trusted sender (normally within an application, all in-process callers are trusted). Messages are not pre-processed in any way to screen for malicious intent. Because of this, the message bus should be configured so that only select accounts can publish to the call topic.

**SECURITY NOTE:** Failure to secure publishing to the topic being consumed by this library will allow publishers to construct malicious messages that can run arbitrary code on the receiving end! See [security](#security) below.

**NOTE:** Functions are asynchronously executed with no mechanism for returning a value to the caller. From the caller's perspective, these functions are "fire and forget". Support for functions that return values may be implemented in a future version.


## Installation

Install from PyPI:

```shell
$ pip install cloud-functions-dispatch
```


## Environment Variables

Two environment variables are required:

**GCP_PROJECT:** this is set by Google in your runtime environment. Locally, just set this to the project name where your topic lives.

**CLOUD_FUNCTIONS_DISPATCH_GCP_PUBSUB_TOPIC:** you will need to provide this value. This is the name of the topic (such as 'my-topic') to subscribe to.

## Sample Usage

The following program demonstrates the basic use of dispatching:

```python
# myapp.py
from cloud_functions_dispatch import dispatch

@dispatch
def my_func(a, b, c):
    if a > b:
        log.warning('a is too large!')
    log.info('a is just right')

def main()
    my_func(1, 2, 3)
```

When you execute this code, and eventually call `main`, you will see something like the following in your local or cloud function logs (depending on where you are running it):

```
I 2020-03-13T22:24:35.427Z my-topic 1043501608491014 pushing function call to pubsub: myapp.my_func
```

... followed shortly by something like this in your cloud function logs, showing the function execution:

```
D 2020-03-13T22:24:35.436557480Z my-topic 1043501608491013 Function execution started
I 2020-03-13T22:24:35.526Z my-topic 1043501608491013 received event 1043501608491013 sent at 2020-03-13T22:24:35.095Z
I 2020-03-13T22:24:35.526Z my-topic 1043501608491013 executing: myapp.my_func
I 2020-03-13T22:24:35.526Z my-topic 1043501608491013 a is just right
D 2020-03-13T22:24:35.527863623Z my-topic 1043501608491013 Function execution took 92 ms, finished with status: 'ok'
```


## Entry Point

Your cloud function will need an entry point. You should use the provided `execute` method:

```python
# main.py
from cloud_functions_dispatch import execute as execute_dispatched
```

Don't forget to include `cloud-functions-dispatch` in your `requirements.txt` as well.

Your codebase should then be deployed to Cloud Functions with the entrypoint specified:

```sh
$ gcloud functions deploy ${FUNCTION_NAME} --trigger-topic=${TOPIC_NAME} --source=${DIR} --entry-point=execute_dispatched ...
```


## Full Example

A complete, working sample can be found in the `sample` directory. To see it in action:

* Create a pubsub topic in GCP (the command below assumes it's `my-topic`)
* Enable the Cloud Functions API in GCP
* Pick an unused name for your function (the command below assumes it's `my-func`)

Then run the following command:

```sh
$ gcloud functions deploy my-func --trigger-topic=my-topic --source=sample --entry-point=execute_dispatched --runtime=python37 --memory=128MB --max-instances=1 --set-env-vars CLOUD_FUNCTIONS_DISPATCH_GCP_PUBSUB_TOPIC=my-topic
```

Now set `GCP_PROJECT` and `CLOUD_FUNCTIONS_DISPATCH_GCP_PUBSUB_TOPIC` locally and:

```sh
$ cd sample
$ PYTHONPATH=..:$PYTHONPATH python -c "import functions; functions.echo(1, 2, x=7)"
```

After a few seconds you will see the output of your cloud function showing the arguments passed.


## <a name="security"></a>Security Considerations

Failure to secure publishing to the topic being consumed by this library will allow publishers to construct malicious messages that can run arbitrary code on the receiving end. This is due to a design choice of Python's `pickle` library, which unpickles in a way that unpacks and executes code if the serialized object contains any. This library will never construct a payload with executable components, but an attacker could do so.

In theory, this is no different than the assumption within a process that all other code in the process can be trusted. In the case of `cloud_function_dispatch`, data that would normally go to the stack instead gets published to a message bus. Consequently, that message bus must be as secure as the rest of the process space. In practice, this just means that you are trusting all actors with permission to publish to the dispatch topic.

I am very open to pull requests in this area.


## Supported Cloud Platforms

Right now support is only included for Google Cloud Platform. I am very open to pull requests that introduce support for any others (AWS and Azure especially). See [issue 1](https://github.com/seawolf42/cloud-functions-dispatch/issues/1) and feel free to comment on that ticket if you are interested in helping out.


## Other Considerations

Sometimes a function will fail. Since there is no mechanism for returning values, this must be handled by the callee. Tasks should be simple and straightforward.

Functions may be invoked more than once (as per Google's SLA on PubSub message handling). Functions should be idempotent (able to be repeated multiple times without introducing errors in the result).

Because the functions being called are implemented in the caller's codebase, the cloud function you deploy to handle dispatched calls should include the caller's codebase. The basic idea is that you have a single codebase but deployed twice: once to cloud functions (the callee) and once as a regular deployment to Kubernetes, some other cloud function, or elsewhere.  Only the subset of the code that implements the functions needs to be included in the callee, so the right architecture can help minimize deployable sizes. Realistically, though, many project won't have enough code to make this an issue.


## Troubleshooting

Common sources of errors:

* import problems in your cloud function
    * make sure you have `cloud-functions-dispatch` in your requirements.txt file
    * relative imports are non-trivial in your top-level modules i


## Contributing

Pull requests are welcome, espeically if they address issues filed against the project.

Local tests are run by typing `make test` in the project folder. You will need `pytest` and a few other packages installed; the `setup.py` is not fully configured to run tests with `pytest` yet. See [issue 3](https://github.com/seawolf42/cloud-functions-dispatch/issues/3) if you know how to integrate this into the traditional `python setup.py test` mechanism.
