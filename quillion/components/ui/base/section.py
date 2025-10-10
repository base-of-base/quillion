from typing import Optional, Callable
from ..element import Element


class Section(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("section", *children, class_name=class_name, **kwargs)


def section(*children, **kwargs):
    return Section(*children, **kwargs)
