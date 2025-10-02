import pytest
import re
from unittest.mock import Mock
import inspect

from quillion import page


class TestPageDecorator:
    def setup_method(self):
        from quillion.pages.base import PageMeta
        PageMeta._registry.clear()
        PageMeta._dynamic_routes.clear()
        PageMeta._regex_routes.clear()
    
    def test_page_decorator_with_sync_function(self):
        @page("/sync-route")
        def sync_page():
            return "Sync Page Content"
        
        assert inspect.isclass(sync_page)
        assert hasattr(sync_page, 'router')
        assert sync_page.router == "/sync-route"
        assert hasattr(sync_page, '_priority')
        assert sync_page._priority == 0
        
        page_instance = sync_page()
        result = page_instance.render()
        assert result == "Sync Page Content"
    
    def test_page_decorator_with_async_function(self):
        @page("/async-route")
        async def async_page():
            return "Async Page Content"
        
        assert inspect.isclass(async_page)
        assert async_page.router == "/async-route"
        
        page_instance = async_page()
        
        async def test_async_render():
            result = await page_instance.render()
            assert result == "Async Page Content"
        
        import asyncio
        asyncio.run(test_async_render())
    
    def test_page_decorator_with_priority(self):
        @page("/priority-route", priority=10)
        def priority_page():
            return "Priority Page"
        
        assert priority_page.router == "/priority-route"
        assert priority_page._priority == 10
    
    def test_page_decorator_with_pattern_route(self):
        pattern = re.compile(r"/item/\d+")
        
        @page(pattern)
        def pattern_page():
            return "Pattern Page"
        
        assert pattern_page.router == pattern
        
        from quillion.pages.base import PageMeta
        found = False
        for registry in [PageMeta._registry, PageMeta._dynamic_routes, PageMeta._regex_routes]:
            for key in registry:
                if registry[key][0] == pattern_page:
                    found = True
                    break
            if found:
                break
        assert found, "Pattern-based page should be registered"
    
    def test_page_decorator_with_parameters(self):
        @page("/params-route")
        def params_page(id: int, name: str = "default"):
            return f"ID: {id}, Name: {name}"
        
        page_instance = params_page()
        
        result = page_instance.render(id=123, name="test")
        assert result == "ID: 123, Name: test"
    
        result = page_instance.render(id=456)
        assert result == "ID: 456, Name: default"
    
    def test_page_decorator_pydantic_validation(self):
        @page("/validation-route")
        def validation_page(id: int, count: int = 1):
            return f"ID: {id}, Count: {count}"
        
        page_instance = validation_page()
        
        result = page_instance.render(id=123, count=5)
        assert result == "ID: 123, Count: 5"
        
        with pytest.raises(Exception):
            page_instance.render(id="not-an-int")
    
    def test_page_decorator_class_name(self):
        @page("/named-route")
        def my_custom_page():
            return "Named Page"
        
        assert my_custom_page.__name__ == "my_custom_page"
    
    def test_page_decorator_inheritance(self):
        @page("/inheritance-route")
        def inheritance_page():
            return "Inheritance Page"
        
        from quillion.pages.base import Page
        assert issubclass(inheritance_page, Page)
    
    def test_page_decorator_metaclass(self):
        @page("/meta-route")
        def meta_page():
            return "Meta Page"
        
        from quillion.pages.base import PageMeta
        assert type(meta_page) == PageMeta
    
    def test_multiple_page_decorators(self):
        @page("/page-one")
        def page_one():
            return "Page One"
        
        @page("/page-two")
        def page_two():
            return "Page Two"
        
        from quillion.pages.base import PageMeta
        page_one_found = False
        page_two_found = False
        
        for registry in [PageMeta._registry, PageMeta._dynamic_routes, PageMeta._regex_routes]:
            for key, (page_class, priority) in (registry.items() if hasattr(registry, 'items') else []):
                if page_class == page_one:
                    page_one_found = True
                if page_class == page_two:
                    page_two_found = True
        
        assert page_one_found, "Page one should be registered"
        assert page_two_found, "Page two should be registered"
    
    def test_page_decorator_with_complex_return_type(self):
        mock_element = Mock()
        
        @page("/complex-route")
        def complex_page():
            return mock_element
        
        page_instance = complex_page()
        result = page_instance.render()
        assert result == mock_element
    
    def test_page_decorator_route_registration(self):
        @page("/registered-route", priority=5)
        def registered_page():
            return "Registered"
        
        from quillion.pages.base import PageMeta
        assert "/registered-route" in PageMeta._registry
        page_class, priority = PageMeta._registry["/registered-route"]
        assert page_class == registered_page
        assert priority == 5
    
    @pytest.mark.asyncio
    async def test_async_page_with_parameters(self):
        @page("/async-params")
        async def async_params_page(user_id: int, action: str = "view"):
            return f"User {user_id} performed {action}"
        
        page_instance = async_params_page()
        result = await page_instance.render(user_id=789, action="edit")
        assert result == "User 789 performed edit"
    
    def test_page_decorator_with_dynamic_route(self):
        @page("/users/[id]")
        def dynamic_page():
            return "Dynamic Page"
        
        assert dynamic_page.router == "/users/[id]"
        
        from quillion.pages.base import PageMeta
        found = False
        for registry in [PageMeta._registry, PageMeta._dynamic_routes, PageMeta._regex_routes]:
            for key in registry:
                if registry[key][0] == dynamic_page:
                    found = True
                    break
            if found:
                break
        assert found, "Dynamic route page should be registered"
    
    def test_page_decorator_with_catch_all_route(self):
        @page("/docs/[...slug]")
        def catch_all_page():
            return "Catch All Page"
        
        assert catch_all_page.router == "/docs/[...slug]"
        
        from quillion.pages.base import PageMeta
        found = False
        for registry in [PageMeta._registry, PageMeta._dynamic_routes, PageMeta._regex_routes]:
            for key in registry:
                if registry[key][0] == catch_all_page:
                    found = True
                    break
            if found:
                break
        assert found, "Catch-all route page should be registered"


class TestPageDecoratorIntegration:    
    def setup_method(self):
        from quillion.pages.base import PageMeta
        PageMeta._registry.clear()
        PageMeta._dynamic_routes.clear()
        PageMeta._regex_routes.clear()
    
    def test_page_decorator_with_component_return(self):
        from quillion.components.base import Component
        
        mock_component = Mock(spec=Component)
        
        @page("/component-route")
        def component_page():
            return mock_component
        
        page_instance = component_page()
        result = page_instance.render()
        assert result == mock_component
    
    def test_page_decorator_with_element_return(self):
        from quillion.components.ui.element import Element
        
        mock_element = Mock(spec=Element)
        
        @page("/element-route")
        def element_page():
            return mock_element
        
        page_instance = element_page()
        result = page_instance.render()
        assert result == mock_element
    
    def test_page_decorator_preserves_function_metadata(self):
        def original_function():
            return "Original"
        
        decorated_page = page("/metadata-route")(original_function)
        
        assert decorated_page.__name__ == "original_function"
    
    def test_page_decorator_with_lambda(self):
        lambda_page = page("/lambda-route")(lambda: "Lambda Page")
        
        assert inspect.isclass(lambda_page)
        page_instance = lambda_page()
        result = page_instance.render()
        assert result == "Lambda Page"


class TestPageDecoratorEdgeCases:
    def test_page_decorator_with_no_parameters(self):
        @page("/no-params")
        def no_params():
            return "No Params"
        
        page_instance = no_params()
        result = page_instance.render()
        assert result == "No Params"
    
    def test_page_decorator_with_star_args(self):
        @page("/star-args")
        def star_args(*args, **kwargs):
            return f"Args: {args}, Kwargs: {kwargs}"
        
        page_instance = star_args()
        result = page_instance.render(param1="value1", param2="value2")
        assert "param1" in result and "value1" in result
    
    def test_page_decorator_nested_function(self):
        def create_page(route):
            @page(route)
            def nested_page():
                return f"Page at {route}"
            return nested_page
        
        custom_page = create_page("/nested-route")
        page_instance = custom_page()
        result = page_instance.render()
        assert result == "Page at /nested-route"
    

class TestPageDecoratorValidation:
    def test_page_decorator_parameter_validation(self):
        @page("/validation-test")
        def validation_test_page(required: int, optional: str = "default"):
            return f"Required: {required}, Optional: {optional}"
        
        page_instance = validation_test_page()
        
        result = page_instance.render(required=42)
        assert result == "Required: 42, Optional: default"
        
        with pytest.raises(Exception):
            page_instance.render(required="not-an-int")
    
    def test_page_decorator_with_type_hints(self):
        from typing import List, Optional
        
        @page("/type-hints")
        def type_hints_page(
            items: List[str],
            count: int,
            optional: Optional[float] = None
        ):
            return f"Items: {items}, Count: {count}, Optional: {optional}"
        
        page_instance = type_hints_page()
        
        result = page_instance.render(items=["a", "b"], count=2, optional=3.14)
        assert "a" in result and "b" in result and "3.14" in result


class TestPageDecoratorPerformance:
    def test_page_decorator_creation_speed(self):
        import time
        
        start_time = time.time()
        
        for i in range(100):
            @page(f"/route-{i}")
            def temp_page():
                return f"Page {i}"
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        assert creation_time < 1.0, f"Page creation too slow: {creation_time}s"
    
    @pytest.mark.asyncio
    async def test_concurrent_async_pages(self):
        @page("/async-concurrent-1")
        async def async_page_1():
            await asyncio.sleep(0.01)
            return "Page 1"
        
        @page("/async-concurrent-2") 
        async def async_page_2():
            await asyncio.sleep(0.01)
            return "Page 2"
        
        page1_instance = async_page_1()
        page2_instance = async_page_2()
        
        import asyncio
        results = await asyncio.gather(
            page1_instance.render(),
            page2_instance.render()
        )
        
        assert results == ["Page 1", "Page 2"]