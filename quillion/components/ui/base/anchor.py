from typing import Optional, Callable
from ..element import Element


class Anchor(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("a", *children, class_name=class_name, **kwargs)


def anchor(*children, **kwargs):
    return Anchor(*children, **kwargs)
