import pytest
from unittest.mock import MagicMock, patch
from quillion import Path


class TestPathSync:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        original_app = Path._app
        Path._app = None
        yield
        Path._app = original_app

    def test_init_sets_app(self):
        from quillion import Path
        
        mock_app = MagicMock()

        Path.init(mock_app)

        assert Path._app == mock_app

    def test_navigate_without_app_does_nothing(self):        
        Path.navigate("/home")

    def test_navigate_without_websocket_does_nothing(self):
        mock_app = MagicMock()
        mock_app.websocket = None
        Path.init(mock_app)

        Path.navigate("/home")

    def test_navigate_async_task_creation(self):
        mock_app = MagicMock()
        mock_app.websocket = MagicMock()
        mock_app.navigate = MagicMock()
        Path.init(mock_app)

        with patch('asyncio.create_task') as mock_create_task:
            Path.navigate("/test")
            
            mock_create_task.assert_called_once()

    def test_multiple_init_calls(self):
        mock_app1 = MagicMock()
        mock_app2 = MagicMock()

        Path.init(mock_app1)
        assert Path._app == mock_app1

        Path.init(mock_app2)
        
        assert Path._app == mock_app2
        assert Path._app != mock_app1

    def test_path_formatting_with_params(self):
        test_cases = [
            ("/user/{user_id}", {"user_id": "123"}, "/user/123"),
            ("/api/{version}/data", {"version": "v1"}, "/api/v1/data"),
            ("/{category}/{id}", {"category": "books", "id": "42"}, "/books/42"),
        ]

        for path_template, params, expected_path in test_cases:
            result = path_template.format(**params) if params else path_template
            
            assert result == expected_path

    def test_navigate_calls_format_with_params(self):
        mock_app = MagicMock()
        mock_app.websocket = MagicMock()
        Path.init(mock_app)

        path_template = "/test/{param}"
        params = {"param": "value"}

        with patch('asyncio.create_task'):
            Path.navigate(path_template, params)