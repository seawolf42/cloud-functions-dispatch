import logging

from cloud_functions_dispatch import dispatch


log = logging.getLogger(__name__)


@dispatch
def echo(*args, **kwargs):
    log.info('echo called with args=%s, kwargs=%s', args, kwargs)


@dispatch
def my_func(a, b, cheer='hooray!'):
    if a > b:
        log.warning('a is too large!')
    else:
        log.info('a is just right: %s', cheer)
