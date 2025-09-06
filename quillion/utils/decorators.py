from typing import Callable, Union, Pattern
import inspect
from pydantic import validate_arguments


def page(route: Union[str, Pattern], priority: int = 0):
    from ..pages.base import Page, PageMeta

    def decorator(func: Callable):
        validated_func = validate_arguments(func)
        is_async = inspect.iscoroutinefunction(func)

        class GeneratedPage(Page, metaclass=PageMeta):
            router = route
            _priority = priority

            if is_async:
                async def render(self, **params):
                    return await validated_func(**params)
            else:
                def render(self, **params):
                    return validated_func(**params)

        GeneratedPage.__name__ = func.__name__
        return GeneratedPage

    return decorator
