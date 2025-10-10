from typing import Optional, Callable
from ..element import Element


class Label(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("label", *children, class_name=class_name, **kwargs)


def label(*children, **kwargs):
    return Label(*children, **kwargs)
