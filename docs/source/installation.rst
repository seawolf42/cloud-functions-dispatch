Installation
============

Install from PyPI:

.. code-block:: sh

    $ pip install cloud-functions-dispatch

Two environment variables are required to import the library:

``GCP_PROJECT``: set by Google in your runtime environment; for local use, set this to the project name where your topic lives

``CLOUD_FUNCTIONS_DISPATCH_GCP_PUBSUB_TOPIC``: the name of the topic (such as ``my-topic``) that will be used for sending and receiving dispatched calls.
