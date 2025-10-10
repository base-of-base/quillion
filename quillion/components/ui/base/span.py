from typing import Optional, Callable
from ..element import Element


class Span(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("span", *children, class_name=class_name, **kwargs)


def span(*children, **kwargs):
    return Span(*children, **kwargs)
