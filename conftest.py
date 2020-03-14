
import os
import sys

import mock
import pytest


BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ['GCP_PROJECT'] = 'test-project'
os.environ['CLOUD_FUNCTIONS_DISPATCH_GCP_PUBSUB_TOPIC'] = 'test-topic'


_mocks = []
for module, attr in (
    # (google.cloud, 'pubsub_v1'),
):
    m = mock.MagicMock()
    setattr(module, attr, m)
    _mocks.append(m)


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    for m in _mocks:
        m.reset_mock()
