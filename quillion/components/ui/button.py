from typing import Optional, Callable
from .element import Element


class Button(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("button", *children, class_name=class_name, **kwargs)


def button(*children, **kwargs):
    return Button(*children, **kwargs)