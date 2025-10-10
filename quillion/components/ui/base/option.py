from typing import Optional, Callable
from ..element import Element


class Option(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("option", *children, class_name=class_name, **kwargs)


def option(*children, **kwargs):
    return Option(*children, **kwargs)
