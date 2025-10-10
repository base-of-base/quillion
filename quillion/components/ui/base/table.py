from typing import Optional, Callable
from ..element import Element


class Table(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("table", *children, class_name=class_name, **kwargs)


def table(*children, **kwargs):
    return Table(*children, **kwargs)
