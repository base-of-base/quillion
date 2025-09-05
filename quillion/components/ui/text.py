from typing import Optional
from .element import Element


class Text(Element):
    def __init__(self, *children, **kwargs):
        super().__init__("p", *children, **kwargs)


def text(*children, **kwargs):
    return Text(*children, **kwargs)
