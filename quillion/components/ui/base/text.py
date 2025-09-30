from typing import Optional
from ..element import Element


class Text(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("p", *children, class_name=class_name, **kwargs)


def text(*children, **kwargs):
    return Text(*children, **kwargs)
