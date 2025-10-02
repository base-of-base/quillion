import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
import websockets
from quillion.core.messaging import Messaging


class TestMessaging:
    @pytest.fixture
    def messaging(self):
        mock_app = Mock()
        return Messaging(mock_app)

    @pytest.fixture
    def mock_websocket(self):
        websocket = AsyncMock(spec=websockets.WebSocketServerProtocol)
        websocket.remote_address = ("127.0.0.1", 8080)
        return websocket

    @pytest.fixture
    def mock_callback(self):
        return Mock()

    @pytest.fixture
    def mock_async_callback(self):
        async def async_callback(*args):
            return "async_result"
        return async_callback

    def test_initialization(self, messaging):
        assert messaging.app is not None
        assert hasattr(messaging, 'app')

    @pytest.mark.asyncio
    async def test_process_inner_message_callback_sync(self, messaging, mock_websocket, mock_callback):
        callback_id = "test_callback_123"
        inner_data = {
            "action": "callback",
            "id": callback_id
        }
        
        messaging.app.callbacks = {callback_id: mock_callback}
        messaging.app.render_current_page = AsyncMock()

        await messaging.process_inner_message(mock_websocket, inner_data)

        mock_callback.assert_called_once()
        messaging.app.render_current_page.assert_called_once_with(mock_websocket)

    @pytest.mark.asyncio
    async def test_process_inner_message_callback_async(self, messaging, mock_websocket, mock_async_callback):
        callback_id = "test_callback_456"
        inner_data = {
            "action": "callback",
            "id": callback_id
        }
        
        messaging.app.callbacks = {callback_id: mock_async_callback}
        messaging.app.render_current_page = AsyncMock()

        await messaging.process_inner_message(mock_websocket, inner_data)

        messaging.app.render_current_page.assert_called_once_with(mock_websocket)

    @pytest.mark.asyncio
    async def test_process_inner_message_callback_not_found(self, messaging, mock_websocket):
        inner_data = {
            "action": "callback",
            "id": "non_existent_callback"
        }
        
        messaging.app.callbacks = {}
        messaging.app.render_current_page = AsyncMock()

        await messaging.process_inner_message(mock_websocket, inner_data)

        messaging.app.render_current_page.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_inner_message_event_callback_with_data(self, messaging, mock_websocket, mock_callback):
        callback_id = "test_event_callback_123"
        event_data = {"value": "test_value", "checked": True}
        inner_data = {
            "action": "event_callback",
            "id": callback_id,
            "event_data": json.dumps(event_data)
        }
        
        messaging.app.callbacks = {callback_id: mock_callback}
        messaging.app.render_current_page = AsyncMock()

        await messaging.process_inner_message(mock_websocket, inner_data)

        mock_callback.assert_called_once_with(event_data)
        messaging.app.render_current_page.assert_called_once_with(mock_websocket)

    @pytest.mark.asyncio
    async def test_process_inner_message_event_callback_without_data(self, messaging, mock_websocket, mock_callback):
        callback_id = "test_event_callback_456"
        inner_data = {
            "action": "event_callback",
            "id": callback_id,
            "event_data": ""
        }
        
        messaging.app.callbacks = {callback_id: mock_callback}
        messaging.app.render_current_page = AsyncMock()

        await messaging.process_inner_message(mock_websocket, inner_data)

        mock_callback.assert_called_once_with({})
        messaging.app.render_current_page.assert_called_once_with(mock_websocket)

    @pytest.mark.asyncio
    async def test_process_inner_message_event_callback_no_parameters(self, messaging, mock_websocket):
        callback_id = "test_event_callback_789"
        
        def callback_without_params():
            return "result"
        
        inner_data = {
            "action": "event_callback",
            "id": callback_id,
            "event_data": json.dumps({"value": "test"})
        }
        
        messaging.app.callbacks = {callback_id: callback_without_params}
        messaging.app.render_current_page = AsyncMock()

        await messaging.process_inner_message(mock_websocket, inner_data)

        messaging.app.render_current_page.assert_called_once_with(mock_websocket)

    @pytest.mark.asyncio
    async def test_process_inner_message_event_callback_invalid_json(self, messaging, mock_websocket, mock_callback):
        callback_id = "test_event_callback_999"
        inner_data = {
            "action": "event_callback",
            "id": callback_id,
            "event_data": "invalid json {"
        }
        
        messaging.app.callbacks = {callback_id: mock_callback}
        messaging.app.render_current_page = AsyncMock()

        await messaging.process_inner_message(mock_websocket, inner_data)

        mock_callback.assert_called_once_with({})
        messaging.app.render_current_page.assert_called_once_with(mock_websocket)

    @pytest.mark.asyncio
    async def test_process_inner_message_event_callback_async(self, messaging, mock_websocket, mock_async_callback):
        callback_id = "test_event_callback_async"
        event_data = {"value": "async_test"}
        inner_data = {
            "action": "event_callback",
            "id": callback_id,
            "event_data": json.dumps(event_data)
        }
        
        messaging.app.callbacks = {callback_id: mock_async_callback}
        messaging.app.render_current_page = AsyncMock()

        await messaging.process_inner_message(mock_websocket, inner_data)

        messaging.app.render_current_page.assert_called_once_with(mock_websocket)

    @pytest.mark.asyncio
    async def test_process_inner_message_event_callback_not_found(self, messaging, mock_websocket):
        inner_data = {
            "action": "event_callback",
            "id": "non_existent_event_callback",
            "event_data": json.dumps({"value": "test"})
        }
        
        messaging.app.callbacks = {}
        messaging.app.render_current_page = AsyncMock()

        await messaging.process_inner_message(mock_websocket, inner_data)

        messaging.app.render_current_page.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_inner_message_navigate(self, messaging, mock_websocket):
        test_path = "/test-path"
        inner_data = {
            "action": "navigate",
            "path": test_path
        }
        
        messaging.app.navigate = AsyncMock()

        await messaging.process_inner_message(mock_websocket, inner_data)

        messaging.app.navigate.assert_called_once_with(test_path, mock_websocket)

    @pytest.mark.asyncio
    async def test_process_inner_message_navigate_empty_path(self, messaging, mock_websocket):
        inner_data = {
            "action": "navigate",
            "path": ""
        }
        
        messaging.app.navigate = AsyncMock()

        await messaging.process_inner_message(mock_websocket, inner_data)

        messaging.app.navigate.assert_called_once_with("", mock_websocket)

    @pytest.mark.asyncio
    async def test_process_inner_message_navigate_no_path(self, messaging, mock_websocket):
        inner_data = {
            "action": "navigate"
        }
        
        messaging.app.navigate = AsyncMock()

        await messaging.process_inner_message(mock_websocket, inner_data)

        messaging.app.navigate.assert_called_once_with("/", mock_websocket)

    @pytest.mark.asyncio
    async def test_process_inner_message_client_error(self, messaging, mock_websocket):
        error_traceback = "Error: Something went wrong\n    at line 123"
        inner_data = {
            "action": "client_error",
            "error": error_traceback
        }

        with patch('builtins.print') as mock_print:
            await messaging.process_inner_message(mock_websocket, inner_data)

            expected_calls = [
                mock_call(f"\n[{mock_websocket.remote_address[0]}:{mock_websocket.remote_address[1]}] Error occurred"),
                mock_call(error_traceback)
            ]
            assert mock_print.call_count == 2
            assert any(call[0][0] == f"\n[{mock_websocket.remote_address[0]}:{mock_websocket.remote_address[1]}] Error occurred" 
                      for call in mock_print.call_args_list)
            assert any(call[0][0] == error_traceback for call in mock_print.call_args_list)

    @pytest.mark.asyncio
    async def test_process_inner_message_client_error_no_traceback(self, messaging, mock_websocket):
        inner_data = {
            "action": "client_error"
        }

        with patch('builtins.print') as mock_print:
            await messaging.process_inner_message(mock_websocket, inner_data)

            assert mock_print.call_count >= 1
            address_printed = any(
                f"[{mock_websocket.remote_address[0]}:{mock_websocket.remote_address[1]}] Error occurred" in str(call)
                for call in mock_print.call_args_list
            )
            assert address_printed

    @pytest.mark.asyncio
    async def test_process_inner_message_unknown_action(self, messaging, mock_websocket):
        inner_data = {
            "action": "unknown_action",
            "some_data": "value"
        }

        with patch('builtins.print') as mock_print:
            await messaging.process_inner_message(mock_websocket, inner_data)

            mock_print.assert_called_once_with(
                f"[{mock_websocket.remote_address[0]}:{mock_websocket.remote_address[1]}] Unknown action: unknown_action"
            )

    @pytest.mark.asyncio
    async def test_process_inner_message_no_action(self, messaging, mock_websocket):
        inner_data = {
            "some_data": "value"
        }

        with patch('builtins.print') as mock_print:
            await messaging.process_inner_message(mock_websocket, inner_data)

            mock_print.assert_called_once_with(
                f"[{mock_websocket.remote_address[0]}:{mock_websocket.remote_address[1]}] Unknown action: None"
            )

    @pytest.mark.asyncio
    async def test_process_inner_message_callback_exception(self, messaging, mock_websocket, mock_callback):
        callback_id = "error_callback"
        inner_data = {
            "action": "callback",
            "id": callback_id
        }
        
        mock_callback.side_effect = Exception("Callback error")
        messaging.app.callbacks = {callback_id: mock_callback}
        messaging.app.render_current_page = AsyncMock()

        with pytest.raises(Exception, match="Callback error"):
            await messaging.process_inner_message(mock_websocket, inner_data)

        messaging.app.render_current_page.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_inner_message_event_callback_exception(self, messaging, mock_websocket, mock_callback):
        callback_id = "error_event_callback"
        inner_data = {
            "action": "event_callback",
            "id": callback_id,
            "event_data": json.dumps({"value": "test"})
        }
        
        mock_callback.side_effect = Exception("Event callback error")
        messaging.app.callbacks = {callback_id: mock_callback}
        messaging.app.render_current_page = AsyncMock()

        with pytest.raises(Exception, match="Event callback error"):
            await messaging.process_inner_message(mock_websocket, inner_data)

        messaging.app.render_current_page.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_inner_message_navigate_exception(self, messaging, mock_websocket):
        inner_data = {
            "action": "navigate",
            "path": "/test"
        }
        
        messaging.app.navigate = AsyncMock(side_effect=Exception("Navigate error"))

        with pytest.raises(Exception, match="Navigate error"):
            await messaging.process_inner_message(mock_websocket, inner_data)

    @pytest.mark.asyncio
    async def test_process_inner_message_event_callback_different_signatures(self, messaging, mock_websocket):
        callback_id = "signature_test"
        
        def callback_with_one_param(event_data):
            return f"Received: {event_data}"
        
        def callback_with_multiple_params(event_data, second_param=None):
            return f"Received: {event_data}, {second_param}"
        
        def callback_with_no_params():
            return "No params"
        
        test_cases = [
            (callback_with_one_param, {"value": "test"}),
            (callback_with_multiple_params, {"value": "test"}),
            (callback_with_no_params, {"value": "test"}),
        ]
        
        for callback, event_data in test_cases:
            messaging.app.callbacks = {callback_id: callback}
            messaging.app.render_current_page = AsyncMock()
            
            inner_data = {
                "action": "event_callback",
                "id": callback_id,
                "event_data": json.dumps(event_data)
            }
            
            await messaging.process_inner_message(mock_websocket, inner_data)
            
            messaging.app.render_current_page.reset_mock()

    @pytest.mark.asyncio
    async def test_process_inner_message_empty_data(self, messaging, mock_websocket):
        inner_data = {}

        with patch('builtins.print') as mock_print:
            await messaging.process_inner_message(mock_websocket, inner_data)

            mock_print.assert_called_once_with(
                f"[{mock_websocket.remote_address[0]}:{mock_websocket.remote_address[1]}] Unknown action: None"
            )

    @pytest.mark.asyncio
    async def test_process_inner_message_none_data(self, messaging, mock_websocket):
        inner_data = None

        with pytest.raises(AttributeError, match="'NoneType' object has no attribute 'get'"):
            with patch('builtins.print'):
                await messaging.process_inner_message(mock_websocket, inner_data)

    @pytest.mark.asyncio
    async def test_process_inner_message_different_websocket_address(self, messaging):
        test_addresses = [
            ("192.168.1.1", 9090),
            ("10.0.0.1", 8080),
            ("localhost", 3000),
        ]
        
        for ip, port in test_addresses:
            websocket = AsyncMock(spec=websockets.WebSocketServerProtocol)
            websocket.remote_address = (ip, port)
            
            inner_data = {
                "action": "client_error",
                "error": "Test error"
            }

            with patch('builtins.print') as mock_print:
                await messaging.process_inner_message(websocket, inner_data)

                address_found = any(
                    f"[{ip}:{port}] Error occurred" in str(call)
                    for call in mock_print.call_args_list
                )
                assert address_found, f"Expected address [{ip}:{port}] not found in print calls"


def mock_call(*args, **kwargs):
    return ((args, kwargs),)