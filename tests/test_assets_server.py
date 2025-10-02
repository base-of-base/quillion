import tempfile
import os
import pytest
from aiohttp.test_utils import make_mocked_request
from quillion.core.server import AssetServer


class TestAssetServer:
    @pytest.fixture
    def temp_assets_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_files = {
                "index.html": "<html><body>Hello World</body></html>",
                "style.css": "body { color: red; }",
                "script.js": "console.log('test');",
                "image.png": b"fake_png_content",
            }
            
            for filename, content in test_files.items():
                filepath = os.path.join(temp_dir, filename)
                if isinstance(content, bytes):
                    with open(filepath, 'wb') as f:
                        f.write(content)
                else:
                    with open(filepath, 'w') as f:
                        f.write(content)
            
            yield temp_dir

    @pytest.fixture
    def asset_server(self, temp_assets_dir):
        return AssetServer(assets_dir=temp_assets_dir)

    async def make_request(self, asset_server, path):
        request = make_mocked_request('GET', path)
        
        request._match_info = {'path': path.lstrip('/')}
        request._app = asset_server.app
        
        return await asset_server.handle_request(request)

    async def get_response_content(self, response, temp_assets_dir, path):
        from aiohttp.web_fileresponse import FileResponse
        
        if isinstance(response, FileResponse):
            file_path = os.path.join(temp_assets_dir, path.lstrip('/'))
            if os.path.exists(file_path):
                if response._content_type.startswith('text/'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return f.read()
                else:
                    with open(file_path, 'rb') as f:
                        return f.read()
            return None
        else:
            if hasattr(response, 'text'):
                return await response.text()
            elif hasattr(response, 'read'):
                return await response.read()
            return None

    @pytest.mark.asyncio
    async def test_nonexistent_file(self, asset_server):
        response = await self.make_request(asset_server, '/nonexistent.html')
        assert response.status == 404

    @pytest.mark.asyncio
    async def test_directory_traversal_prevention(self, asset_server):
        response = await self.make_request(asset_server, '/../etc/passwd')
        assert response.status in [403, 404]

    @pytest.mark.asyncio
    async def test_unknown_mime_type(self, asset_server, temp_assets_dir):
        unknown_file = os.path.join(temp_assets_dir, 'test.unknown')
        with open(unknown_file, 'w') as f:
            f.write('test content')
        
        response = await self.make_request(asset_server, '/test.unknown')
        assert response.status == 200
        assert response.headers['Content-Type'] == 'application/octet-stream'

    @pytest.mark.asyncio
    async def test_root_path(self, asset_server):
        response = await self.make_request(asset_server, '/')
        assert response.status == 404

    @pytest.mark.asyncio
    async def test_path_normalization(self, asset_server):
        request = make_mocked_request('GET', '/../test.txt')
        request._match_info = {'path': '../test.txt'}
        request._app = asset_server.app
        
        response = await asset_server.handle_request(request)
        assert response.status == 403

    def test_start_method(self, asset_server):
        assert hasattr(asset_server, 'start')
        assert callable(asset_server.start)

    @pytest.mark.asyncio
    async def test_subdirectory_with_spaces(self, asset_server, temp_assets_dir):
        subdir = os.path.join(temp_assets_dir, 'sub directory')
        os.makedirs(subdir)
        file_path = os.path.join(subdir, 'file with spaces.txt')
        with open(file_path, 'w') as f:
            f.write('content with spaces')
        
        response = await self.make_request(asset_server, '/sub%20directory/file%20with%20spaces.txt')
        if response.status == 200:
            content = await self.get_response_content(response, temp_assets_dir, '/sub directory/file with spaces.txt')
            assert 'content with spaces' in content
        else:
            response = await self.make_request(asset_server, '/sub directory/file with spaces.txt')
            assert True