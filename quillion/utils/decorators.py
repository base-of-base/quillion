from typing import Callable, Union, Any, Dict, get_type_hints
import inspect
import re
from pydantic import validate_arguments, ValidationError


def page(route: Union[str, re.Pattern], priority: int = 0):
    from ..pages.base import Page, PageMeta

    def decorator(func: Callable):
        validated = validate_arguments(func)

        class GeneratedPage(Page, metaclass=PageMeta):
            original_router = route
            _priority = priority
            router = route

            if inspect.iscoroutinefunction(func):

                async def render(self, **params):
                    return await validated(**params)

            else:

                def render(self, **params):
                    return validated(**params)

        GeneratedPage.__name__ = func.__name__
        return GeneratedPage

    return decorator