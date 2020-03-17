.. _security:

Security Considerations
=======================

Failure to secure publishing to the topic being consumed by this library will allow publishers to construct malicious messages that can run arbitrary code on the receiving end. This is due to a design choice of Python's `pickle` library, which unpickles in a way that unpacks and executes code if the serialized object contains any. This library will never construct a payload with executable components, but an attacker could do so.

In theory, this is no different than the assumption within a process that all other code in the process can be trusted. In the case of ``cloud_function_dispatch``, data that would normally go to the stack instead gets published to a message bus. Consequently, that message bus must be as secure as the rest of the process space. In practice, this just means that you are trusting all actors with permission to publish to the dispatch topic.

I am very open to pull requests in this area.
