from typing import Optional, Callable
from ..element import Element


class Link(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("link", *children, class_name=class_name, **kwargs)


def link(*children, **kwargs):
    return Link(*children, **kwargs)
