import pytest
import json
import os
import websockets
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from quillion import Quillion
from quillion.utils.finder import RouteFinder
from quillion.core.crypto import Crypto
from quillion.core.messaging import Messaging
from quillion.core.server import AssetServer, ServerConnection
from quillion.pages.base import Page

class TestQuillion:
    @pytest.fixture
    def quillion(self):
        with patch.dict(os.environ, {
            "QUILLION_ASSET_HOST": "localhost",
            "QUILLION_ASSET_PORT": "1338",
            "QUILLION_ASSET_PATH": "/test/assets"
        }):
            return Quillion()

    @pytest.fixture
    def mock_websocket(self):
        websocket = AsyncMock(spec=websockets.WebSocketServerProtocol)
        websocket.remote_address = ("127.0.0.1", 8080)
        websocket.path = "/test"
        return websocket

    @pytest.fixture
    def mock_page(self):
        page = Mock(spec=Page)
        page._rendered_component_keys = Mock()
        page._rendered_component_keys.clear = Mock()
        page._component_instance_cache = {}
        page.params = {}
        page.get_page_class_name.return_value = "test-page"
        page._cleanup_old_component_instances = Mock()
        page.render.return_value = Mock()
        return page

    @pytest.fixture
    def mock_container_class(self):
        with patch('quillion.core.app.Container') as mock_container:
            container_instance = Mock()
            container_instance.to_dict.return_value = {"tag": "div", "children": []}
            container_instance.add_class = Mock()
            mock_container.return_value = container_instance
            yield mock_container

    def test_singleton_pattern(self):
        Quillion._instance = None
        
        instance1 = Quillion()
        instance2 = Quillion._instance
        
        assert instance1 is instance2
        assert Quillion._instance is instance1

    def test_initialization(self, quillion):
        assert quillion.callbacks == {}
        assert quillion.current_page is None
        assert quillion.current_path is None
        assert quillion.assets_path == "/test/assets"
        assert quillion.asset_server_url == "http://localhost:1338"
        assert isinstance(quillion.asset_server, AssetServer)
        assert quillion.websocket is None
        assert quillion._state_instances == {}
        assert quillion.style_tag_id == "quillion-dynamic-styles"
        assert quillion._current_rendering_page is None
        assert isinstance(quillion.crypto, Crypto)
        assert isinstance(quillion.messaging, Messaging)
        assert isinstance(quillion.server_connection, ServerConnection)
        assert quillion.external_css_files == []
        assert quillion._css_cache == {}


    @pytest.mark.asyncio
    async def test_handler_key_exchange_failure(self, quillion, mock_websocket):
        test_data = {"action": "public_key", "key": "test_key"}
        
        with patch.object(quillion.crypto, 'handle_key_exchange', AsyncMock(return_value=False)):
            with patch("quillion_cli.debug.debugger.debugger") as mock_debugger:
                mock_websocket.recv.return_value = json.dumps(test_data)
                
                await quillion.handler(mock_websocket)
                
                quillion.crypto.handle_key_exchange.assert_called_once_with(mock_websocket, test_data)
                mock_debugger.info.assert_called()

    @pytest.mark.asyncio
    async def test_navigate_https_redirect(self, quillion, mock_websocket):
        test_url = "https://example.com"
        
        with patch.object(quillion.crypto, 'encrypt_response', return_value={"encrypted": "data"}):
            await quillion.navigate(test_url, mock_websocket)
            
            quillion.crypto.encrypt_response.assert_called_once_with(
                mock_websocket, 
                {"action": "redirect", "url": test_url}
            )

    @pytest.mark.asyncio
    async def test_navigate_route_found_new_page(self, quillion, mock_websocket, mock_page):
        test_path = "/test"
        
        with patch.object(RouteFinder, 'find_route', return_value=(mock_page.__class__, {}, None)):
            with patch.object(quillion, 'render_current_page', AsyncMock()) as mock_render:
                with patch("quillion_cli.debug.debugger.debugger") as mock_debugger:
                    
                    await quillion.navigate(test_path, mock_websocket)
                    
                    RouteFinder.find_route.assert_called_once_with(test_path)
                    mock_render.assert_called_once_with(mock_websocket)
                    assert quillion.current_page is not None
                    assert quillion.current_path == test_path
                    mock_debugger.info.assert_called()

    @pytest.mark.asyncio
    async def test_navigate_route_found_same_page(self, quillion, mock_websocket, mock_page):
        test_path = "/test"
        quillion.current_page = mock_page
        
        with patch.object(RouteFinder, 'find_route', return_value=(mock_page.__class__, {}, None)):
            with patch.object(quillion, 'render_current_page', AsyncMock()) as mock_render:
                with patch("quillion_cli.debug.debugger.debugger") as mock_debugger:
                    
                    await quillion.navigate(test_path, mock_websocket)
                    
                    RouteFinder.find_route.assert_called_once_with(test_path)
                    mock_render.assert_called_once_with(mock_websocket)
                    assert quillion.current_page is mock_page
                    mock_debugger.info.assert_called()

    @pytest.mark.asyncio
    async def test_navigate_route_not_found(self, quillion, mock_websocket):
        test_path = "/unknown"
        
        with patch.object(RouteFinder, 'find_route', return_value=(None, None, None)):
            with patch("quillion_cli.debug.debugger.debugger") as mock_debugger:
                
                await quillion.navigate(test_path, mock_websocket)
                
                RouteFinder.find_route.assert_called_once_with(test_path)
                mock_debugger.error.assert_called_once_with(f"[127.0.0.1:8080] Received unknown path: {test_path}")

    def test_redirect_no_websocket(self, quillion):
        quillion.websocket = None
        test_path = "/redirect"
        
        quillion.redirect(test_path)

    @pytest.mark.asyncio
    async def test_render_current_page_no_page_or_websocket(self, quillion):
        await quillion.render_current_page(Mock())
        
        quillion.current_page = Mock()
        await quillion.render_current_page(None)
        

    @pytest.mark.asyncio
    async def test_render_current_page_exception(self, quillion, mock_websocket, mock_page):
        quillion.current_page = mock_page
        mock_page.render.side_effect = Exception("Render error")
        
        with patch("quillion_cli.debug.debugger.debugger"):
            try:
                await quillion.render_current_page(mock_websocket)
            except Exception:
                pass
            
            assert quillion._current_rendering_page is None

    def test_css_method(self, quillion):
        css_files = ["style1.css", "style2.css"]
        
        result = quillion.css(css_files)
        
        assert quillion.external_css_files == css_files
        assert result is quillion
        
        more_files = ["style3.css"]
        quillion.css(more_files)
        assert quillion.external_css_files == css_files + more_files

    def test_start_method(self, quillion):
        with patch.object(quillion.asset_server, 'start') as mock_asset_start:
            with patch.object(quillion.server_connection, 'start') as mock_server_start:
                
                quillion.start(
                    host="127.0.0.1",
                    port=8080,
                    assets_port=9000,
                    assets_host="assets.local"
                )
                
                mock_asset_start.assert_called_once_with(host="assets.local", port=9000)
                mock_server_start.assert_called_once_with(quillion.handler, "127.0.0.1", 8080)

    def test_start_method_with_env_vars(self, quillion):
        with patch.dict(os.environ, {
            "QUILLION_HOST": "env_host",
            "QUILLION_PORT": "9999",
            "QUILLION_ASSET_PORT": "8888",
            "QUILLION_ASSET_HOST": "env_assets"
        }):
            with patch.object(quillion.asset_server, 'start') as mock_asset_start:
                with patch.object(quillion.server_connection, 'start') as mock_server_start:
                    
                    quillion.start()
                    
                    mock_asset_start.assert_called_once_with(host="env_assets", port=8888)
                    mock_server_start.assert_called_once_with(quillion.handler, "env_host", 9999)
                    assert quillion.asset_server_url == "http://env_assets:8888"

    def test_multiple_instances_cleanup(self, quillion, mock_websocket):
        quillion._state_instances = {Mock: Mock()}
        quillion.crypto.client_aes_keys = {mock_websocket: b"test_key"}
        
        quillion._state_instances.clear()
        quillion.crypto.cleanup(mock_websocket)
        
        assert quillion._state_instances == {}
        assert mock_websocket not in quillion.crypto.client_aes_keys

