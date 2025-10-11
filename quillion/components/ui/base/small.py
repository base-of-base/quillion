from typing import Optional, Callable
from ..element import Element


class Small(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("small", *children, class_name=class_name, **kwargs)


def small(*children, **kwargs):
    return Small(*children, **kwargs)
