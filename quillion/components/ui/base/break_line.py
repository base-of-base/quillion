from typing import Optional, Callable
from ..element import Element


class Break(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("br", *children, class_name=class_name, **kwargs)


def break_line(*children, **kwargs):
    return Break(*children, **kwargs)
