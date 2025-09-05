from typing import Optional, Callable
from .element import Element


class Button(Element):
    def __init__(self, *children, **kwargs):
        super().__init__("button", *children, **kwargs)


def button(*children, **kwargs):
    return Button(*children, **kwargs)
