import re
from re import Pattern
from quillion.utils.regex_parser import RegexParser, RouteType


class TestRegexParser:
    def test_compile_route_regex_pattern(self):
        pattern = re.compile(r"^/test/\d+$")
        compiled_pattern, route_type = RegexParser.compile_route(pattern)

        assert compiled_pattern == pattern
        assert route_type == RouteType.REGEX_PATTERN

    def test_compile_route_regex_string(self):
        pattern, route_type = RegexParser.compile_route(r"regex:^/user/\d+$")

        assert isinstance(pattern, Pattern)
        assert pattern.pattern == r"^/user/\d+$"
        assert route_type == RouteType.REGEX_STRING

    def test_compile_route_regex_string_with_whitespace(self):
        pattern, route_type = RegexParser.compile_route(r"regex: ^/test/\w+ $")

        assert isinstance(pattern, Pattern)
        assert pattern.pattern == r"^/test/\w+ $"
        assert route_type == RouteType.REGEX_STRING

    def test_compile_route_catch_all(self):
        pattern, route_type = RegexParser.compile_route(".*")
        assert isinstance(pattern, Pattern)
        assert pattern.pattern == ".*"
        assert route_type == RouteType.CATCH_ALL

        pattern, route_type = RegexParser.compile_route("*")
        assert isinstance(pattern, Pattern)
        assert pattern.pattern == ".*"
        assert route_type == RouteType.CATCH_ALL

    def test_compile_route_dynamic_with_braces(self):
        pattern, route_type = RegexParser.compile_route("/users/{id}")

        assert isinstance(pattern, Pattern)
        assert pattern.pattern == r"^/users/(?P<id>[^\/]+)$"
        assert route_type == RouteType.DYNAMIC

    def test_compile_route_dynamic_with_star(self):
        pattern, route_type = RegexParser.compile_route("/users/*")

        assert isinstance(pattern, Pattern)
        assert pattern.pattern == r"^/users/[^\/]+$"
        assert route_type == RouteType.DYNAMIC

    def test_compile_route_dynamic_complex(self):
        pattern, route_type = RegexParser.compile_route("/users/{id}/posts/{post_id}")

        assert isinstance(pattern, Pattern)
        expected_pattern = r"^/users/(?P<id>[^\/]+)/posts/(?P<post_id>[^\/]+)$"
        assert pattern.pattern == expected_pattern
        assert route_type == RouteType.DYNAMIC

    def test_compile_route_dynamic_mixed_syntax(self):
        pattern, route_type = RegexParser.compile_route("/users/{id}/*/edit")

        assert isinstance(pattern, Pattern)
        expected_pattern = r"^/users/(?P<id>[^\/]+)/[^\/]+/edit$"
        assert pattern.pattern == expected_pattern
        assert route_type == RouteType.DYNAMIC

    def test_compile_route_static(self):
        pattern, route_type = RegexParser.compile_route("/static/route")

        assert isinstance(pattern, Pattern)
        assert pattern.pattern == r"^/static/route$"
        assert route_type == RouteType.STATIC

    def test_compile_route_static_with_special_chars(self):
        pattern, route_type = RegexParser.compile_route(
            "/user.com/path+with$special.chars"
        )

        assert isinstance(pattern, Pattern)
        expected = r"^/user\.com/path\+with\$special\.chars$"
        assert pattern.pattern == expected
        assert route_type == RouteType.STATIC

    def test_get_route_type_regex_pattern(self):
        pattern = re.compile(r"test")
        route_type = RegexParser.get_route_type(pattern)
        assert route_type == RouteType.REGEX_PATTERN

    def test_get_route_type_regex_string(self):
        route_type = RegexParser.get_route_type(r"regex:^test$")
        assert route_type == RouteType.REGEX_STRING

    def test_get_route_type_catch_all(self):
        assert RegexParser.get_route_type(".*") == RouteType.CATCH_ALL
        assert RegexParser.get_route_type("*") == RouteType.CATCH_ALL

    def test_get_route_type_dynamic(self):
        test_cases = [
            "/users/{id}",
            "/posts/*",
            "/api/{version}/*/endpoint",
            "category/{cat_id}/item/*",
        ]

        for route in test_cases:
            route_type = RegexParser.get_route_type(route)
            assert route_type == RouteType.DYNAMIC

    def test_get_route_type_static(self):
        test_cases = ["/", "/users", "/api/v1/endpoint", "/static/path/here"]

        for route in test_cases:
            route_type = RegexParser.get_route_type(route)
            assert route_type == RouteType.STATIC

    def test_extract_params_with_match(self):
        pattern = re.compile(r"^/users/(?P<id>\w+)/posts/(?P<post_id>\d+)$")
        params = RegexParser.extract_params(pattern, "/users/john/posts/123")

        assert params == {"id": "john", "post_id": "123"}

    def test_extract_params_without_named_groups(self):
        pattern = re.compile(r"^/static/path$")
        params = RegexParser.extract_params(pattern, "/static/path")

        assert params == {}

    def test_extract_params_no_match(self):
        pattern = re.compile(r"^/users/\d+$")
        params = RegexParser.extract_params(pattern, "/users/abc")

        assert params is None

    def test_extract_params_empty_path(self):
        pattern = re.compile(r"^/$")
        params = RegexParser.extract_params(pattern, "/")

        assert params == {}

    def test_get_clean_class_name_from_static_string(self):
        class_name = RegexParser.get_clean_class_name("/api/v1/users")
        assert class_name == "api-v1-users"

    def test_get_clean_class_name_from_dynamic_string(self):
        class_name = RegexParser.get_clean_class_name("/users/{id}/posts")
        assert class_name == "users-id-posts"

    def test_get_clean_class_name_empty_route(self):
        assert RegexParser.get_clean_class_name("/") == "dynamic"
        assert RegexParser.get_clean_class_name("") == "dynamic"

    def test_get_clean_class_name_regex_prefix_only(self):
        assert RegexParser.get_clean_class_name("regex:") == "dynamic"

    def test_get_clean_class_name_complex_regex(self):
        pattern = re.compile(r"^/api/v[\d]+/users/(?P<id>\w+)$")
        class_name = RegexParser.get_clean_class_name(pattern)

        assert "api" in class_name
        assert "v" in class_name
        assert "users" in class_name
        assert "id" in class_name


class TestRegexParserIntegration:
    def test_complete_workflow_static_route(self):
        route = "/api/users"

        pattern, route_type = RegexParser.compile_route(route)
        assert route_type == RouteType.STATIC

        direct_route_type = RegexParser.get_route_type(route)
        assert direct_route_type == RouteType.STATIC

        params = RegexParser.extract_params(pattern, "/api/users")
        assert params == {}

        class_name = RegexParser.get_clean_class_name(route)
        assert class_name == "api-users"

    def test_complete_workflow_dynamic_route(self):
        route = "/users/{user_id}/posts/{post_id}"

        pattern, route_type = RegexParser.compile_route(route)
        assert route_type == RouteType.DYNAMIC

        direct_route_type = RegexParser.get_route_type(route)
        assert direct_route_type == RouteType.DYNAMIC

        params = RegexParser.extract_params(pattern, "/users/123/posts/456")
        assert params == {"user_id": "123", "post_id": "456"}

        class_name = RegexParser.get_clean_class_name(route)
        assert class_name == "users-user_id-posts-post_id"

    def test_complete_workflow_regex_route(self):
        route = r"regex:^/item/\d+$"

        pattern, route_type = RegexParser.compile_route(route)
        assert route_type == RouteType.REGEX_STRING

        direct_route_type = RegexParser.get_route_type(route)
        assert direct_route_type == RouteType.REGEX_STRING

        params = RegexParser.extract_params(pattern, "/item/789")
        assert params == {}

        class_name = RegexParser.get_clean_class_name(route)
        assert "item" in class_name.lower()

    def test_complete_workflow_catch_all_route(self):
        route = ".*"

        pattern, route_type = RegexParser.compile_route(route)
        assert route_type == RouteType.CATCH_ALL

        direct_route_type = RegexParser.get_route_type(route)
        assert direct_route_type == RouteType.CATCH_ALL

        params = RegexParser.extract_params(pattern, "/any/path/here")
        assert params == {}

        class_name = RegexParser.get_clean_class_name(route)
        assert class_name == "dynamic"


class TestRegexParserEdgeCases:
    def test_compile_route_empty_string(self):
        pattern, route_type = RegexParser.compile_route("")
        assert pattern.pattern == "^$"
        assert route_type == RouteType.STATIC

    def test_compile_route_only_slash(self):
        pattern, route_type = RegexParser.compile_route("/")
        assert pattern.pattern == r"^/$"
        assert route_type == RouteType.STATIC

    def test_compile_route_multiple_braces(self):
        pattern, route_type = RegexParser.compile_route("/{a}/{b}/{c}")
        expected = r"^/(?P<a>[^\/]+)/(?P<b>[^\/]+)/(?P<c>[^\/]+)$"
        assert pattern.pattern == expected
        assert route_type == RouteType.DYNAMIC

    def test_compile_route_escaped_braces(self):
        pattern, route_type = RegexParser.compile_route("/users/{not_dynamic}")
        assert route_type == RouteType.DYNAMIC

    def test_extract_params_with_unicode(self):
        pattern = re.compile(r"^/users/(?P<name>.+)$")
        params = RegexParser.extract_params(pattern, "/users/用户名")
        assert params == {"name": "用户名"}

    def test_extract_params_with_special_chars_in_params(self):
        pattern = re.compile(r"^/path/(?P<param>[^/]+)$")
        params = RegexParser.extract_params(pattern, "/path/hello-world_123.test")
        assert params == {"param": "hello-world_123.test"}

    def test_get_clean_class_name_very_long_route(self):
        long_route = "/" + "a" * 100 + "/" + "b" * 100
        class_name = RegexParser.get_clean_class_name(long_route)

        assert isinstance(class_name, str)
        assert len(class_name) > 0

    def test_get_clean_class_name_only_special_chars(self):
        class_name = RegexParser.get_clean_class_name("/@#$%^&*()/")
        assert class_name == "dynamic"


class TestRegexParserPatternMatching:
    def test_static_route_matching(self):
        pattern, _ = RegexParser.compile_route("/exact/path")

        assert RegexParser.extract_params(pattern, "/exact/path") == {}

        assert RegexParser.extract_params(pattern, "/exact/path/extra") is None
        assert RegexParser.extract_params(pattern, "/exact") is None
        assert RegexParser.extract_params(pattern, "/different/path") is None

    def test_dynamic_route_matching(self):
        pattern, _ = RegexParser.compile_route("/users/{id}/edit")

        params = RegexParser.extract_params(pattern, "/users/123/edit")
        assert params == {"id": "123"}

        assert RegexParser.extract_params(pattern, "/users/123") is None
        assert RegexParser.extract_params(pattern, "/users/123/edit/extra") is None
        assert RegexParser.extract_params(pattern, "/users//edit") is None

    def test_catch_all_matching(self):
        pattern, _ = RegexParser.compile_route(".*")

        test_paths = ["/", "/any", "/any/path", "/deep/nested/path", ""]

        for path in test_paths:
            params = RegexParser.extract_params(pattern, path)
            assert params == {}

    def test_regex_pattern_matching(self):
        pattern, _ = RegexParser.compile_route(re.compile(r"^/api/v(\d+)/.*$"))

        params = RegexParser.extract_params(pattern, "/api/v1/users")
        assert params == {}

        params = RegexParser.extract_params(pattern, "/api/v2/posts")
        assert params == {}

        assert RegexParser.extract_params(pattern, "/api/vx/users") is None

    def test_regex_string_matching(self):
        pattern, _ = RegexParser.compile_route(r"regex:^/item/(?P<id>\d+)$")

        params = RegexParser.extract_params(pattern, "/item/123")
        assert params == {"id": "123"}

        assert RegexParser.extract_params(pattern, "/item/abc") is None


class TestRegexParserBehavior:
    def test_forward_slash_escaping_behavior(self):
        test_cases = [
            ("/simple", r"^/simple$"),
            ("/path/with/slashes", r"^/path/with/slashes$"),
            ("/users/{id}", r"^/users/(?P<id>[^\/]+)$"),
            ("/api/*/endpoint", r"^/api/[^\/]+/endpoint$"),
        ]

        for route, expected_pattern in test_cases:
            pattern, _ = RegexParser.compile_route(route)
            assert pattern.pattern == expected_pattern


class TestRegexParserCorrected:
    def test_actual_dynamic_route_patterns(self):
        test_cases = [
            ("/users/{id}", r"^/users/(?P<id>[^\/]+)$"),
            ("/posts/*", r"^/posts/[^\/]+$"),
            ("/api/{version}/endpoint", r"^/api/(?P<version>[^\/]+)/endpoint$"),
        ]

        for route, expected_pattern in test_cases:
            pattern, route_type = RegexParser.compile_route(route)
            assert pattern.pattern == expected_pattern
            assert route_type == RouteType.DYNAMIC
