from typing import Optional
from .element import Element


class Image(Element):
    def __init__(self, *children, **kwargs):
        super().__init__("img", *children, **kwargs)


def image(*children, **kwargs):
    return Image(*children, **kwargs)
