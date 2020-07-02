import base64
import functools
import gzip
import inspect
import logging
import os
import pickle

from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import List

from google.cloud import pubsub_v1


log = logging.getLogger(__name__)


GCP_PROJECT = os.environ.get('GCP_PROJECT')
PUBSUB_TOPIC = os.environ.get('CLOUD_FUNCTIONS_DISPATCH_GCP_PUBSUB_TOPIC')


assert GCP_PROJECT, 'environment variable GCP_PROJECT must be set'
assert PUBSUB_TOPIC, 'environment variable CLOUD_FUNCTIONS_DISPATCH_GCP_PUBSUB_TOPIC'


def dispatch(func):
    name = f'{func.__module__}.{func.__qualname__}'
    if name in _functions:
        log.error('duplicate registration of: %s', name)
        raise KeyError('function with same name already exists')
    _functions[name] = func
    signature = inspect.signature(func)

    @functools.wraps(func)
    def send(*args, **kwargs):
        log.debug('calling remote function: %s', name)
        signature.bind(*args, **kwargs)
        _send_to_remote(_F(name=name, args=args, kwargs=kwargs))

    send.__name__ = f'{name}_dispatch'

    log.debug('registered: %s', send.__name__)
    return send


def execute(event, context):
    log.info('received event %s sent at %s', context.event_id, context.timestamp)
    try:
        _receive_from_remote(base64.b64decode(event['data']))
    except Exception as e:
        log.exception('unable to complete remote function call: %s', e)
        # this should return an appropriate value to pubsub to indicate a failure


_publisher = pubsub_v1.PublisherClient()
_topic = _publisher.topic_path(GCP_PROJECT, PUBSUB_TOPIC)


@dataclass
class _F():

    name: str
    args: List[Any]
    kwargs: Dict[str, Any]

    def __str__(self):
        return self.name


_functions = dict()


def _pack(f):
    log.debug('packing: %s', f)
    compressed = gzip.compress(pickle.dumps(f))
    log.debug('compressed size: %s -> %d', f, len(compressed))
    return compressed


def _unpack(data):
    return pickle.loads(gzip.decompress(data))


def _send_to_remote(f):
    log.info('pushing function call to pubsub: %s', f)
    _publisher.publish(_topic, _pack(f))


def _receive_from_remote(data):
    log.debug('receiving function call to execute')
    f = _unpack(data)
    log.info('executing: %s', f)
    _functions[f.name](*f.args, **f.kwargs)


@dispatch
def ping_show_args(*args, **kwargs):
    log.info('dispatched function called with: %s %s', args, kwargs)


@dispatch
def ping_forward_to_show_args(*args, **kwargs):
    log.info('forwarding function call to show_args: %s %s', args, kwargs)
    ping_show_args(*args, **kwargs)
