Other Considerations
====================

A few additional points to keep in mind:


Supported Cloud Platforms
-------------------------

Right now support is only included for Google Cloud Platform. I am very open to pull requests that introduce support for any others (AWS and Azure especially). See `issue 1 <https://github.com/seawolf42/cloud-functions-dispatch/issues/1>`_ and feel free to comment on that ticket if you are interested in helping out.


Failures
--------

Sometimes a function will fail. Since there is no mechanism for returning values, this must be handled by the callee. Tasks should be simple and straightforward.

Functions may be invoked more than once (as per Google's SLA on PubSub message handling). Functions should be idempotent (able to be repeated multiple times without introducing errors in the result).

Because the functions being called are implemented in the caller's codebase, the cloud function you deploy to handle dispatched calls should include the caller's codebase. The basic idea is that you have a single codebase but deployed twice: once to cloud functions (the callee) and once as a regular deployment to Kubernetes, some other cloud function, or elsewhere.  Only the subset of the code that implements the functions needs to be included in the callee, so the right architecture can help minimize deployable sizes. Realistically, though, many project won't have enough code to make this an issue.


Troubleshooting
---------------

The most common errors encountered relate to importing. To avoid these:

* Make sure all functions being called belong in modules that are *not* in the ``__main__`` namespace
    * function execution is looked up by registered name; if the application and the cloud function import things in different ways, functions will not discovered properly in the cloud function
    * one easy way to do this is to build your function artifact by copying your app folder to the same directory your function's ``main.py`` is in and zipping and deploying that
* Make sure the cloud function's ``main.py`` file imports (either directly or indirectly) all modules that contain dispatched functions
    * functions are registered when they are imported, but they need to have been registered prior to any calls being received for execution
