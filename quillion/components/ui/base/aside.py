from typing import Optional, Callable
from ..element import Element


class Aside(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("aside", *children, class_name=class_name, **kwargs)


def aside(*children, **kwargs):
    return Aside(*children, **kwargs)
