from typing import Callable
import inspect
import asyncio
from ..pages.base import Page, PageMeta


def page(route: str):
    def decorator(func: Callable):
        is_coroutine = inspect.iscoroutinefunction(func)

        class GeneratedPage(Page, metaclass=PageMeta):
            router = route

            def render(self, **params):
                if is_coroutine:
                    loop = asyncio.get_event_loop()
                    return loop.run_until_complete(func(**params))
                else:
                    return func(**params)

        GeneratedPage.__name__ = func.__name__
        return GeneratedPage

    return decorator
