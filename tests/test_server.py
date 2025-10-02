import asyncio
import pytest
import websockets
from unittest.mock import Mock, patch, MagicMock
from typing import Callable
from quillion import ServerConnection


class TestServerConnection:

    @pytest.fixture
    def server_connection(self):
        return ServerConnection()

    @pytest.fixture
    def mock_handler(self):
        return Mock()

    @pytest.fixture
    def mock_loop(self):
        loop = Mock()

        future = asyncio.Future()
        future.set_result(None)

        def run_until_complete(future_or_coro):
            if asyncio.iscoroutine(future_or_coro):
                try:
                    asyncio.create_task(future_or_coro).cancel()
                except:
                    pass
            return future_or_coro

        def run_forever():
            pass

        loop.run_until_complete = run_until_complete
        loop.run_forever = run_forever

        return loop

    def test_start_creates_websocket_server(
        self, server_connection, mock_handler, mock_loop
    ):
        with patch("websockets.serve") as mock_serve, patch(
            "asyncio.get_event_loop", return_value=mock_loop
        ):

            mock_server_instance = Mock()
            mock_serve.return_value = mock_server_instance

            server_connection.start(mock_handler, "localhost", 8080)

            mock_serve.assert_called_once_with(mock_handler, "localhost", 8080)

    def test_start_uses_default_parameters(
        self, server_connection, mock_handler, mock_loop
    ):
        with patch("websockets.serve") as mock_serve, patch(
            "asyncio.get_event_loop", return_value=mock_loop
        ):

            mock_server_instance = Mock()
            mock_serve.return_value = mock_server_instance

            server_connection.start(mock_handler)

            mock_serve.assert_called_once_with(mock_handler, "0.0.0.0", 1337)

    def test_start_with_custom_host_port(
        self, server_connection, mock_handler, mock_loop
    ):
        with patch("websockets.serve") as mock_serve, patch(
            "asyncio.get_event_loop", return_value=mock_loop
        ):

            mock_server_instance = Mock()
            mock_serve.return_value = mock_server_instance

            server_connection.start(mock_handler, "127.0.0.1", 9000)

            mock_serve.assert_called_once_with(mock_handler, "127.0.0.1", 9000)
