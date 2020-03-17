Overview
========

Cloud Functions Dispatch gives you the ability to dispatch in-process no-response function calls to a remote cloud function by applying a decorator to your function.

This is useful for tasks such as the following:

* update a database record separately from this process
* run secondary processes as side-effects of receiving a request
* fan-out of a large job into chunks that are completed independently

Basically any task that accepts some set of serializable parameters but not any in-process state and does not need to return a value is a great candidate for dispatching.

Functions are asynchronously executed with no mechanism for returning a value to the caller. From the caller's perspective, these functions are "fire and forget". Support for functions that return values may be implemented in a future version.


A note on security
------------------

The library assumes all method calls are from a trusted sender (normally within an application, all in-process callers are trusted). Messages are not pre-processed in any way to screen for malicious intent. Because of this, the message bus should be configured so that only fully-trusted accounts can publish to the call topic.

Failure to secure publishing to the topic being consumed by this library will allow publishers to construct malicious messages that can run arbitrary code within your deployed cloud function! See :ref:`security` for more details.
