from typing import Optional, Callable
from ..element import Element


class TableRow(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("tr", *children, class_name=class_name, **kwargs)


def table_row(*children, **kwargs):
    return TableRow(*children, **kwargs)
