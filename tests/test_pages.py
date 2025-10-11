import pytest
from unittest.mock import Mock, patch
from quillion.pages.base import Page, PageMeta, Component, Element


class TestPageMeta:
    def setup_method(self):
        PageMeta._registry.clear()
        PageMeta._dynamic_routes.clear()
        PageMeta._regex_routes.clear()

    def test_investigate_route_registration(self):
        class StaticPage(Page):
            router = "/static"

            def render(self, **params):
                return Mock(spec=Element)

        class DynamicPage(Page):
            router = "/users/[id]"

            def render(self, **params):
                return Mock(spec=Element)

        class CatchAllPage(Page):
            router = "/docs/[...slug]"

            def render(self, **params):
                return Mock(spec=Element)

        class RegexPage(Page):
            router = r"/item/\d+"

            def render(self, **params):
                return Mock(spec=Element)

        assert "/static" in PageMeta._registry
        assert "/users/[id]" in PageMeta._registry
        assert "/docs/[...slug]" in PageMeta._registry
        found_regex = False
        for route in PageMeta._registry:
            if route == r"/item/\d+":
                found_regex = True
                break
        if not found_regex:
            for pattern in PageMeta._regex_routes:
                if PageMeta._regex_routes[pattern][0] == RegexPage:
                    found_regex = True
                    break
        assert found_regex

    def test_static_route_registration(self):
        class TestPage(Page):
            router = "/static-route"

            def render(self, **params):
                return Mock(spec=Element)

        assert "/static-route" in PageMeta._registry
        page_class, priority = PageMeta._registry["/static-route"]
        assert page_class == TestPage
        assert priority == 0

        assert hasattr(TestPage, "_regex")
        assert hasattr(TestPage, "_route_type")
        assert hasattr(TestPage, "_original_router")

    def test_all_routes_in_main_registry(self):
        class StaticPage(Page):
            router = "/static"

            def render(self, **params):
                return Mock(spec=Element)

        class DynamicPage(Page):
            router = "/users/[id]"

            def render(self, **params):
                return Mock(spec=Element)

        class CatchAllPage(Page):
            router = "/docs/[...slug]"

            def render(self, **params):
                return Mock(spec=Element)

        assert "/static" in PageMeta._registry
        assert "/users/[id]" in PageMeta._registry
        assert "/docs/[...slug]" in PageMeta._registry

        assert PageMeta._registry["/static"][0] == StaticPage
        assert PageMeta._registry["/users/[id]"][0] == DynamicPage
        assert PageMeta._registry["/docs/[...slug]"][0] == CatchAllPage

    def test_route_type_attributes_set(self):
        class StaticPage(Page):
            router = "/static"

            def render(self, **params):
                return Mock(spec=Element)

        class DynamicPage(Page):
            router = "/users/[id]"

            def render(self, **params):
                return Mock(spec=Element)

        class RegexPage(Page):
            router = r"/item/\d+"

            def render(self, **params):
                return Mock(spec=Element)

        for page_class in [StaticPage, DynamicPage, RegexPage]:
            assert hasattr(page_class, "_regex")
            assert hasattr(page_class, "_route_type")
            assert hasattr(page_class, "_original_router")
            assert page_class._original_router == page_class.router

    def test_priority_registration(self):
        class HighPriorityPage(Page):
            router = "/high"
            _priority = 10

            def render(self, **params):
                return Mock(spec=Element)

        class LowPriorityPage(Page):
            router = "/low"
            _priority = 1

            def render(self, **params):
                return Mock(spec=Element)

        assert "/high" in PageMeta._registry
        assert "/low" in PageMeta._registry
        assert PageMeta._registry["/high"][1] == 10
        assert PageMeta._registry["/low"][1] == 1

    def test_no_router_no_registration(self):
        initial_registry_count = len(PageMeta._registry)

        class NoRouterPage(Page):
            def render(self, **params):
                return Mock(spec=Element)

        assert len(PageMeta._registry) == initial_registry_count

    def test_router_none_no_registration(self):
        initial_registry_count = len(PageMeta._registry)

        class NoneRouterPage(Page):
            router = None

            def render(self, **params):
                return Mock(spec=Element)

        assert len(PageMeta._registry) == initial_registry_count


class TestPage:
    @pytest.fixture
    def page_without_router(self):
        class TestPage(Page):
            def render(self, **params):
                return Mock(spec=Element)

        return TestPage()

    @pytest.fixture
    def page_with_router(self):
        class TestPage(Page):
            router = "/test"

            def render(self, **params):
                return Mock(spec=Element)

        return TestPage()

    @pytest.fixture
    def page_with_params(self):
        class TestPage(Page):
            router = "/test"

            def render(self, **params):
                return Mock(spec=Element)

        return TestPage(params={"id": "123", "name": "test"})

    def test_page_initialization(self, page_without_router):
        assert page_without_router._component_instance_cache == {}
        assert page_without_router._rendered_component_keys == set()
        assert page_without_router.params == {}

    def test_page_initialization_with_params(self, page_with_params):
        assert page_with_params.params == {"id": "123", "name": "test"}

    def test_render_not_implemented(self):
        class TestPage(Page):
            pass

        with pytest.raises(NotImplementedError):
            TestPage().render()

    def test_get_page_class_name_with_router(self, page_with_router):
        class_name = page_with_router.get_page_class_name()
        assert class_name.startswith("quillion-page-test-")
        assert len(class_name.split("-")[-1]) == 6

    def test_get_page_class_name_without_router(self, page_without_router):
        class_name = page_without_router.get_page_class_name()
        assert class_name.startswith("quillion-page-None-")

    def test_get_page_class_name_cached(self, page_with_router):
        first_call = page_with_router.get_page_class_name()
        second_call = page_with_router.get_page_class_name()
        assert first_call == second_call

    def test_get_page_class_name_uses_original_router(self):
        class TestPage(Page):
            router = "/original"

            def render(self, **params):
                return Mock(spec=Element)

        page = TestPage()
        page._original_router = "/modified"

        class_name = page.get_page_class_name()
        assert "modified" in class_name.lower()

    @patch("quillion.core.app.Quillion._instance")
    def test_get_or_create_component_instance_new(
        self, mock_quillion, page_with_router
    ):
        mock_component = Mock(spec=Component)
        mock_component.key = "test-key"
        mock_component.text = "test text"
        mock_component.css_classes = []
        mock_component.styles = {}

        result = page_with_router._get_or_create_component_instance(mock_component)

        assert result == mock_component
        assert "test-key" in page_with_router._component_instance_cache
        assert "test-key" in page_with_router._rendered_component_keys
        assert hasattr(mock_component, "_rerender_callback")

    @patch("quillion.core.app.Quillion._instance")
    def test_get_or_create_component_instance_existing(
        self, mock_quillion, page_with_router
    ):
        mock_component1 = Mock(spec=Component)
        mock_component1.key = "test-key"
        mock_component1.text = "initial text"
        mock_component1.css_classes = ["class1"]
        mock_component1.styles = {"color": "red"}

        page_with_router._get_or_create_component_instance(mock_component1)

        mock_component2 = Mock(spec=Component)
        mock_component2.key = "test-key"
        mock_component2.text = "updated text"
        mock_component2.css_classes = ["class2"]
        mock_component2.styles = {"background": "blue"}

        result = page_with_router._get_or_create_component_instance(mock_component2)

        assert result == mock_component1
        assert mock_component1.text == "updated text"
        assert "class2" in mock_component1.css_classes
        assert mock_component1.styles["background"] == "blue"

    def test_get_or_create_component_instance_no_key(self, page_with_router):
        mock_component = Mock(spec=Component)
        mock_component.key = None

        result = page_with_router._get_or_create_component_instance(mock_component)

        assert result == mock_component
        assert page_with_router._component_instance_cache == {}
        assert page_with_router._rendered_component_keys == set()

    @patch("quillion.core.app.Quillion._instance")
    def test_cleanup_old_component_instances(self, mock_quillion, page_with_router):
        mock_component1 = Mock(spec=Component)
        mock_component1.key = "key1"
        mock_component2 = Mock(spec=Component)
        mock_component2.key = "key2"

        page_with_router._get_or_create_component_instance(mock_component1)
        page_with_router._get_or_create_component_instance(mock_component2)

        page_with_router._rendered_component_keys.clear()
        page_with_router._cleanup_old_component_instances()

        assert page_with_router._component_instance_cache == {}

    @patch("quillion.core.app.Quillion._instance")
    def test_cleanup_preserves_current_components(
        self, mock_quillion, page_with_router
    ):
        mock_component1 = Mock(spec=Component)
        mock_component1.key = "key1"
        mock_component1._rerender_callback = None

        mock_component2 = Mock(spec=Component)
        mock_component2.key = "key2"
        mock_component2._rerender_callback = None

        page_with_router._get_or_create_component_instance(mock_component1)
        page_with_router._get_or_create_component_instance(mock_component2)

        page_with_router._rendered_component_keys = {"key1"}
        page_with_router._cleanup_old_component_instances()

        assert "key1" in page_with_router._component_instance_cache
        assert "key2" not in page_with_router._component_instance_cache
        assert page_with_router._rendered_component_keys == set()


class TestPageIntegration:
    def setup_method(self):
        PageMeta._registry.clear()
        PageMeta._dynamic_routes.clear()
        PageMeta._regex_routes.clear()

    def test_multiple_pages_coexist(self):
        class Page1(Page):
            router = "/page1"

            def render(self, **params):
                return Mock(spec=Element)

        class Page2(Page):
            router = "/page2"

            def render(self, **params):
                return Mock(spec=Element)

        assert "/page1" in PageMeta._registry
        assert "/page2" in PageMeta._registry
        assert PageMeta._registry["/page1"][0] == Page1
        assert PageMeta._registry["/page2"][0] == Page2

    def test_inheritance_behavior(self):
        class BasePage(Page):
            router = "/base"

            def render(self, **params):
                return Mock(spec=Element)

        class ChildPage(BasePage):
            router = "/child"

        assert "/base" in PageMeta._registry
        assert "/child" in PageMeta._registry
        assert PageMeta._registry["/base"][0] == BasePage
        assert PageMeta._registry["/child"][0] == ChildPage

    @patch("quillion.core.app.Quillion._instance")
    def test_component_lifecycle(self, mock_quillion):
        class TestPage(Page):
            router = "/test"

            def render(self, **params):
                return Mock(spec=Element)

        page = TestPage()

        mock_component = Mock(spec=Component)
        mock_component.key = "test-component"
        mock_component.text = "initial"
        mock_component.css_classes = []
        mock_component.styles = {}

        component1 = page._get_or_create_component_instance(mock_component)
        assert "test-component" in page._component_instance_cache

        mock_component2 = Mock(spec=Component)
        mock_component2.key = "test-component"
        mock_component2.text = "updated"
        mock_component2.css_classes = ["new-class"]
        mock_component2.styles = {"color": "red"}

        component2 = page._get_or_create_component_instance(mock_component2)
        assert component1 == component2
        assert component1.text == "updated"

        page._rendered_component_keys.clear()
        page._cleanup_old_component_instances()
        assert "test-component" not in page._component_instance_cache


class TestRouteMatching:
    def setup_method(self):
        PageMeta._registry.clear()
        PageMeta._dynamic_routes.clear()
        PageMeta._regex_routes.clear()

    def test_find_page_for_static_route(self):
        class StaticPage(Page):
            router = "/static"

            def render(self, **params):
                return Mock(spec=Element)

        assert "/static" in PageMeta._registry
        page_class, _ = PageMeta._registry["/static"]
        assert page_class == StaticPage
