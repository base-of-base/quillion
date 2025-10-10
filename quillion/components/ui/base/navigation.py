from typing import Optional, Callable
from ..element import Element


class Navigation(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("nav", *children, class_name=class_name, **kwargs)


def navigation(*children, **kwargs):
    return Navigation(*children, **kwargs)
