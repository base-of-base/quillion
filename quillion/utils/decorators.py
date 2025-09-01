from typing import Callable
from ..pages.base import Page, PageMeta


def page(route: str):
    def decorator(func: Callable):
        class GeneratedPage(Page, metaclass=PageMeta):
            router = route

            def render(self):
                return func()

        GeneratedPage.__name__ = func.__name__
        return GeneratedPage

    return decorator
