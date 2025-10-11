from typing import Optional, Callable
from ..element import Element


class Legend(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("legend", *children, class_name=class_name, **kwargs)


def legend(*children, **kwargs):
    return Legend(*children, **kwargs)
