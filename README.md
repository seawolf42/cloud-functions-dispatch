# Cloud Functions Dispatch

Cloud Functions Dispatch gives you the ability to dispatch in-process no-response function calls to a remote cloud function by applying a decorator to your function.

This is useful for tasks such as the following:

* update a database record separately from this process
* run secondary processes as side-effects of receiving a request
* fan-out of a large job into chunks that are completed independently

Basically any task that accepts some set of serializable parameters but not any in-process state and does not need to return a value is a great candidate for dispatching.

Functions are asynchronously executed with no mechanism for returning a value to the caller. From the caller's perspective, these functions are "fire and forget". Support for functions that return values may be implemented in a future version.


## Example

Imagine you have a function that you call every time a row in a certain table :

```python
def save(users, context):
    for user in users:
        user.save()
        update_related(user, context)

def update_related(user, context):
    entity = db.retrieve(user.id)
    for item in entity.get_related():
        item.last_updated = context.update_time
        item.save()
```

Note that this code is intentionally inefficient just to demonstrate the point; imagine `update_related` takes 10 seconds per user and you might be doing this for thousands of users at a time. Your process will struggle for resources: time, memory, or threads will be consumed performing the work. Now imagine you are running a job like this every few seconds. Your code will choke.

One approach to handle this case is to send `update_related` to a separate cloud function for execution. But then you have to define the function, marshall data somehow, and then invoke the function. While these tasks are simple in theory, there are several complexities that make them challenging in practice.

Using `cloud_functions_dispatch`, the only change necessary to the code above is decorating `update_related`:

```python
from cloud_functions_dispatch import dispatch

...

@dispatch  # <- this is the only change necessary to make this a remote call
def update_related(user, context):
    entity = db.retrieve(user.id)
    for item in entity.get_related():
        item.last_updated = context.update_time
        item.save()
```

Now every time you call `update_related`, the full parameter list is serialized, compressed, and pushed to PubSub. A cloud function also containing the same function will receive the message and execute the code. 

Refer to the [Project Documentation](https://cloud-functions-dispatch.readthedocs.io/) for installation and usage.
