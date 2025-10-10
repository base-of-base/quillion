from typing import Optional, Callable
from ..element import Element


class TableCell(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("td", *children, class_name=class_name, **kwargs)


def table_cell(*children, **kwargs):
    return TableCell(*children, **kwargs)
