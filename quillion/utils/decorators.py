from typing import Callable, Union
import inspect
import re

def page(route: Union[str, re.Pattern], priority: int = 0):
    from ..pages.base import Page, PageMeta

    def decorator(func: Callable):
        class GeneratedPage(Page, metaclass=PageMeta):
            original_router = route
            _priority = priority
            router = route
            
            if inspect.iscoroutinefunction(func):
                async def render(self, **params):
                    return await func(**params)
            else:
                def render(self, **params):
                    return func(**params)
        
        GeneratedPage.__name__ = func.__name__
        return GeneratedPage
    return decorator
