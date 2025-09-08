from typing import Optional
from .element import Element


class Image(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("img", *children, class_name=class_name, **kwargs)


def image(*children, **kwargs):
    return Image(*children, **kwargs)
