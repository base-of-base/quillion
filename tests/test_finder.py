import pytest
import re
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Tuple, Optional

from quillion.utils.finder import RouteFinder, PageMeta, RegexParser


class TestRouteFinder:
    def setup_method(self):
        PageMeta._registry.clear()
        PageMeta._dynamic_routes.clear()
        PageMeta._regex_routes.clear()
    
    def test_normalize_path_empty(self):
        assert RouteFinder._normalize_path("") == "/"
        assert RouteFinder._normalize_path("/") == "/"
    
    def test_normalize_path_with_content(self):
        assert RouteFinder._normalize_path("users") == "/users"
        assert RouteFinder._normalize_path("/users") == "/users"
        assert RouteFinder._normalize_path("users/") == "/users"
        assert RouteFinder._normalize_path("/users/") == "/users"
        assert RouteFinder._normalize_path("users/profile") == "/users/profile"
        assert RouteFinder._normalize_path("/users/profile/") == "/users/profile"
        
    def test_find_route_no_matching_routes(self):
        page_cls, params, priority = RouteFinder.find_route("/nonexistent")
        
        assert page_cls is None
        assert params is None
        assert priority == float("-inf")
    
    def test_find_route_static_route_match(self):
        mock_page_cls = Mock()
        mock_page_cls._regex = re.compile(r"^/users$")
        
        PageMeta._registry["/users"] = (mock_page_cls, 0)
        
        with patch.object(RegexParser, 'extract_params') as mock_extract:
            mock_extract.return_value = {}
            
            page_cls, params, priority = RouteFinder.find_route("/users")
            
            assert page_cls == mock_page_cls
            assert params == {}
            assert priority == 0
            mock_extract.assert_called_with(mock_page_cls._regex, "/users")
    
    def test_find_route_static_route_priority(self):
        mock_page_low = Mock()
        mock_page_low._regex = re.compile(r"^/users$")
        
        PageMeta._registry["/users"] = (mock_page_low, 5)
        
        with patch.object(RegexParser, 'extract_params') as mock_extract:
            mock_extract.return_value = {}
            
            page_cls, params, priority = RouteFinder.find_route("/users")
            
            assert page_cls == mock_page_low
            assert priority == 5
    
    def test_find_route_dynamic_route_match(self):
        mock_page_cls = Mock()
        pattern = re.compile(r"^/users/(?P<id>\w+)$")
        
        PageMeta._dynamic_routes["/users/[id]"] = (pattern, mock_page_cls, 0)
        
        with patch.object(RegexParser, 'extract_params') as mock_extract:
            mock_extract.return_value = {"id": "123"}
            
            page_cls, params, priority = RouteFinder.find_route("/users/123")
            
            assert page_cls == mock_page_cls
            assert params == {"id": "123"}
            assert priority == 0
            mock_extract.assert_called_with(pattern, "/users/123")
    
    def test_find_route_regex_route_match(self):
        mock_page_cls = Mock()
        pattern = re.compile(r"^/item/\d+$")
        
        PageMeta._regex_routes[pattern] = (mock_page_cls, 0)
        
        with patch.object(RegexParser, 'extract_params') as mock_extract:
            mock_extract.return_value = {}
            
            page_cls, params, priority = RouteFinder.find_route("/item/123")
            
            assert page_cls == mock_page_cls
            assert params == {}
            assert priority == 0
            mock_extract.assert_called_with(pattern, "/item/123")
    
    def test_find_route_priority_order(self):
        mock_page_low = Mock()
        mock_page_high = Mock()
        
        pattern_low = re.compile(r"^/test$")
        pattern_high = re.compile(r"^/test$")
        
        PageMeta._registry["/test"] = (mock_page_low, 5)
        PageMeta._regex_routes[pattern_high] = (mock_page_high, 10)
        
        with patch.object(RegexParser, 'extract_params') as mock_extract:
            mock_extract.return_value = {}
            
            page_cls, params, priority = RouteFinder.find_route("/test")
            
            assert page_cls == mock_page_high
            assert priority == 10
    
    def test_find_route_search_order(self):
        calls = []
        
        mock_page_regex = Mock()
        mock_page_static = Mock()
        mock_page_dynamic = Mock()
        
        pattern_regex = re.compile(r"^/test$")
        pattern_dynamic = re.compile(r"^/test$")
        
        PageMeta._regex_routes[pattern_regex] = (mock_page_regex, 0)
        PageMeta._registry["/test"] = (mock_page_static, 0)
        PageMeta._dynamic_routes["/test"] = (pattern_dynamic, mock_page_dynamic, 0)
        
        def tracked_extract(pattern, path):
            calls.append((pattern, path))
            if len(calls) == 1:
                return {}
            return None
        
        with patch.object(RegexParser, 'extract_params', side_effect=tracked_extract):
            RouteFinder.find_route("/test")
            
            assert len(calls) == 1
            assert calls[0][0] == pattern_regex
    
    def test_find_route_with_params_extraction(self):
        mock_page_cls = Mock()
        mock_page_cls._regex = re.compile(r"^/users/(?P<id>\w+)/posts/(?P<post_id>\d+)$")
        
        PageMeta._registry["/users/[id]/posts/[post_id]"] = (mock_page_cls, 0)
        
        with patch.object(RegexParser, 'extract_params') as mock_extract:
            mock_extract.return_value = {"id": "john", "post_id": "123"}
            
            page_cls, params, priority = RouteFinder.find_route("/users/john/posts/123")
            
            assert page_cls == mock_page_cls
            assert params == {"id": "john", "post_id": "123"}
            assert priority == 0
    
    def test_find_route_no_match_after_extraction(self):
        mock_page_cls = Mock()
        mock_page_cls._regex = re.compile(r"^/users$")
        
        PageMeta._registry["/users"] = (mock_page_cls, 0)
        
        with patch.object(RegexParser, 'extract_params') as mock_extract:
            mock_extract.return_value = None
            
            page_cls, params, priority = RouteFinder.find_route("/users")
            
            assert page_cls is None
            assert params is None
            assert priority == float("-inf")
    
    def test_find_route_multiple_matches_same_priority(self):
        mock_page1 = Mock()
        mock_page2 = Mock()
        
        pattern1 = re.compile(r"^/test$")
        pattern2 = re.compile(r"^/test$")
        
        PageMeta._regex_routes[pattern1] = (mock_page1, 5)
        PageMeta._registry["/test"] = (mock_page2, 5)
        
        with patch.object(RegexParser, 'extract_params') as mock_extract:
            mock_extract.return_value = {}
            
            page_cls, params, priority = RouteFinder.find_route("/test")
            
            assert page_cls == mock_page1
            assert priority == 5
    
    def test_find_route_path_normalization_applied(self):
        mock_page_cls = Mock()
        mock_page_cls._regex = re.compile(r"^/users$")
        
        PageMeta._registry["/users"] = (mock_page_cls, 0)
        
        with patch.object(RegexParser, 'extract_params') as mock_extract:
            mock_extract.return_value = {}
            
            test_paths = ["users", "/users", "users/", "/users/"]
            
            for path in test_paths:
                mock_extract.reset_mock()
                page_cls, params, priority = RouteFinder.find_route(path)
                
                expected_path = RouteFinder._normalize_path(path)
                mock_extract.assert_called_with(mock_page_cls._regex, expected_path)
                assert page_cls == mock_page_cls


class TestRouteFinderIntegration:
    def setup_method(self):
        PageMeta._registry.clear()
        PageMeta._dynamic_routes.clear()
        PageMeta._regex_routes.clear()

    def test_integration_priority_handling(self):
        from quillion.pages.base import Page
        
        class LowPriorityPage(Page):
            router = "/test"
            _priority = 1
            
            def render(self, **params):
                return "Low Priority"
        
        class HighPriorityPage(Page):
            router = "/test"
            _priority = 10
            
            def render(self, **params):
                return "High Priority"
        
        with patch.object(RegexParser, 'extract_params') as mock_extract:
            mock_extract.return_value = {}
            
            page_cls, params, priority = RouteFinder.find_route("/test")
            assert page_cls == HighPriorityPage
            assert priority == 10
    
    def test_integration_complex_route_matching(self):
        from quillion.pages.base import Page
        
        class BlogPostPage(Page):
            router = "/blog/[year]/[month]/[slug]"
            
            def render(self, **params):
                return f"Blog Post: {params}"
        
        with patch.object(RegexParser, 'extract_params') as mock_extract:
            mock_extract.return_value = {"year": "2024", "month": "01", "slug": "my-post"}
            
            page_cls, params, priority = RouteFinder.find_route("/blog/2024/01/my-post")
            assert page_cls == BlogPostPage
            assert params == {"year": "2024", "month": "01", "slug": "my-post"}
            assert priority == 0


class TestRouteFinderEdgeCases:
    def setup_method(self):
        PageMeta._registry.clear()
        PageMeta._dynamic_routes.clear()
        PageMeta._regex_routes.clear()
    
    def test_find_route_with_root_path(self):
        mock_page_cls = Mock()
        mock_page_cls._regex = re.compile(r"^/$")
        
        PageMeta._registry["/"] = (mock_page_cls, 0)
        
        page_cls, params, priority = RouteFinder.find_route("/")
        assert page_cls == mock_page_cls
        assert params == {}
        assert priority == 0
    
    def test_find_route_with_nested_paths(self):
        mock_page_cls = Mock()
        mock_page_cls._regex = re.compile(r"^/a/b/c/d/e/f/g$")
        
        PageMeta._registry["/a/b/c/d/e/f/g"] = (mock_page_cls, 0)
        
        page_cls, params, priority = RouteFinder.find_route("/a/b/c/d/e/f/g")
        assert page_cls == mock_page_cls
        assert params == {}
        assert priority == 0
    
    def test_find_route_special_characters(self):
        mock_page_cls = Mock()
        pattern = re.compile(r"^/users/(?P<id>[\w\-\.]+)$")
        
        PageMeta._dynamic_routes["/users/[id]"] = (pattern, mock_page_cls, 0)
        
        test_cases = [
            ("/users/user-123", {"id": "user-123"}),
            ("/users/user_123", {"id": "user_123"}),
            ("/users/user.123", {"id": "user.123"}),
        ]
        
        for path, expected_params in test_cases:
            with patch.object(RegexParser, 'extract_params') as mock_extract:
                mock_extract.return_value = expected_params
                
                page_cls, params, priority = RouteFinder.find_route(path)
                assert page_cls == mock_page_cls
                assert params == expected_params
    
    def test_find_route_unicode_characters(self):
        mock_page_cls = Mock()
        pattern = re.compile(r"^/users/(?P<id>.+)$")
        
        PageMeta._dynamic_routes["/users/[id]"] = (pattern, mock_page_cls, 0)
        
        with patch.object(RegexParser, 'extract_params') as mock_extract:
            mock_extract.return_value = {"id": "用户123"}
            
            page_cls, params, priority = RouteFinder.find_route("/users/用户123")
            assert page_cls == mock_page_cls
            assert params == {"id": "用户123"}
