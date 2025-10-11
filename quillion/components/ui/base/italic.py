from typing import Optional, Callable
from ..element import Element


class Italic(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("i", *children, class_name=class_name, **kwargs)

def italic(*children, **kwargs):
    return Italic(*children, **kwargs)
