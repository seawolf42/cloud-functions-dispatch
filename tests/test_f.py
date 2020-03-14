import pytest

from cloud_functions_dispatch import f


class TestConfig():

    def test_env_vars(self):
        assert f.GCP_PROJECT == 'test-project'
        assert f.PUBSUB_TOPIC == 'test-topic'

    @pytest.mark.skip
    def test_env_var_missing_gcp_project(self):
        assert False, 'not sure how to validate this yet'

    @pytest.mark.skip
    def test_env_var_missing_cloud_functions_dispatch_gcp_pubsub_topic(self):
        assert False, 'not sure how to validate this yet'


class BaseFunctionsTest():

    def setup_method(self):
        self.instance = f._F(**self._object_data)

    _object_data = dict(
        name='abcdefghijklmnopqrstuvwxyz',
        args=(1, 2, 3, 'a', 'b', 'c'),
        kwargs=dict(x=1, y='y'),
    )


class TestMarshalling(BaseFunctionsTest):

    def test_pack(self, mocker):
        mock_serialized = mocker.MagicMock()
        mock_pickle = mocker.patch('cloud_functions_dispatch.f.pickle')
        mock_pickle.dumps.return_value = mock_serialized
        mock_compressed = mocker.MagicMock()
        mock_gzip = mocker.patch('cloud_functions_dispatch.f.gzip')
        mock_gzip.compress.return_value = mock_compressed
        result = f._pack(self.instance)
        assert result == mock_compressed
        mock_pickle.dumps.assert_called_once_with(self.instance)
        mock_gzip.compress.assert_called_once_with(mock_serialized)

    def test_unpack(self, mocker):
        mock_decompressed = mocker.MagicMock()
        mock_gzip = mocker.patch('cloud_functions_dispatch.f.gzip')
        mock_gzip.decompress.return_value = mock_decompressed
        mock_deserialized = mocker.MagicMock()
        mock_pickle = mocker.patch('cloud_functions_dispatch.f.pickle')
        mock_pickle.loads.return_value = mock_deserialized
        mock_data = mocker.MagicMock()
        result = f._unpack(mock_data)
        assert result == mock_deserialized
        mock_gzip.decompress.assert_called_once_with(mock_data)
        mock_pickle.loads.assert_called_once_with(mock_decompressed)

    def test_pack_unpack_inverse(self, mocker):
        assert f._unpack(f._pack(self.instance)) == self.instance


class TestCalling(BaseFunctionsTest):

    def test_send_to_remote(self, mocker):
        mock_publisher = mocker.patch('cloud_functions_dispatch.f._publisher')
        mock_topic = mocker.patch('cloud_functions_dispatch.f._topic')
        mock_packed = mocker.MagicMock()
        mock_pack = mocker.patch('cloud_functions_dispatch.f._pack', return_value=mock_packed)
        f._send_to_remote(self.instance)
        mock_pack.assert_called_once_with(self.instance)
        mock_publisher.publish.assert_called_once_with(mock_topic, mock_packed)

    def test_receive_from_remote(self, mocker):
        mock_data = mocker.MagicMock()
        mock_unpacked = self.instance
        mock_unpack = mocker.patch('cloud_functions_dispatch.f._unpack', return_value=mock_unpacked)
        mock_fn = mocker.MagicMock()
        mocker.patch.dict('cloud_functions_dispatch.f._functions', values={self.instance.name: mock_fn})
        f._receive_from_remote(mock_data)
        mock_unpack.assert_called_once_with(mock_data)
        mock_fn.assert_called_once_with(*self.instance.args, **self.instance.kwargs)


def _test_undecorated(): pass


@f.dispatch
def _test_function_with_arguments_decorated(a1, a2, a3, a4, a5, a6, x=42, y='z'): pass


class TestPublishing(BaseFunctionsTest):

    def test_dispatch(self, mocker):
        function = _test_undecorated
        expected_name = f'{function.__module__}.{function.__qualname__}'
        mock_send_fn = mocker.patch('cloud_functions_dispatch.f._send_to_remote')
        mock_signature = mocker.MagicMock(bind=mocker.MagicMock())
        mock_inspect = mocker.patch('cloud_functions_dispatch.f.inspect')
        mock_inspect.signature = mocker.MagicMock(return_value=mock_signature)
        result = f.dispatch(function)
        assert f._functions[expected_name] == function
        assert result.__name__ == f'{expected_name}_dispatch'
        mock_inspect.signature.assert_called_once_with(function)
        mock_args = self._object_data.get('args')
        mock_kwargs = self._object_data.get('kwargs')
        result(*mock_args, **mock_kwargs)
        mock_signature.bind.assert_called_once_with(*mock_args, **mock_kwargs)
        mock_send_fn.assert_called_once_with(
            f._F(name=expected_name, args=self.instance.args, kwargs=self.instance.kwargs),
        )

    def test_dispatch_repeated_name(self, mocker):
        function = _test_undecorated
        expected_name = f'{function.__module__}.{function.__qualname__}'
        mocker.patch.dict('cloud_functions_dispatch.f._functions', values={expected_name: True})
        with pytest.raises(KeyError):
            f.dispatch(function)

    def test_dispatching_function_validates_arg_list(self, mocker):
        function = _test_function_with_arguments_decorated
        mocker.patch('cloud_functions_dispatch.f._send_to_remote')
        function(*self.instance.args, **self.instance.kwargs)
        with pytest.raises(TypeError):
            function(1, 3)

    def test_execute(self, mocker):
        mock_decoded = mocker.MagicMock()
        mock_decoder = mocker.patch('base64.b64decode', return_value=mock_decoded)
        mock_receive = mocker.patch('cloud_functions_dispatch.f._receive_from_remote')
        mock_data = mocker.MagicMock()
        mock_event = dict(data=mock_data)
        f.execute(mock_event, mocker.MagicMock())
        mock_decoder.assert_called_once_with(mock_data)
        mock_receive.assert_called_once_with(mock_decoded)

    def test_execute_exception(self, mocker):
        mocker.patch('base64.b64decode')
        mocker.patch('cloud_functions_dispatch.f._receive_from_remote', side_effect=RuntimeError)
        mock_data = mocker.MagicMock()
        mock_event = dict(data=mock_data)
        f.execute(mock_event, mocker.MagicMock())

    @pytest.mark.skip
    def test_execute_exception_return_value(self):
        assert False, 'not sure how to validate this yet'
