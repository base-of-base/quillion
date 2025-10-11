from typing import Optional, Callable
from ..element import Element


class Strikethrough(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("s", *children, class_name=class_name, **kwargs)


def strikethrough(*children, **kwargs):
    return Strikethrough(*children, **kwargs)
