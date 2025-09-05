# quillion\utils\decorators.py

from typing import Callable
import inspect
import asyncio
from ..pages.base import Page, PageMeta


def page(route: str):
    def decorator(func: Callable):
        class GeneratedPage(Page, metaclass=PageMeta):
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