from typing import Optional, Callable
from ..element import Element


class Input(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("input", *children, class_name=class_name, **kwargs)


def input(*children, **kwargs):
    return Input(*children, **kwargs)
