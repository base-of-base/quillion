from typing import Optional, Callable
from ..element import Element


class Code(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("code", *children, class_name=class_name, **kwargs)


def code(*children, **kwargs):
    return Code(*children, **kwargs)
