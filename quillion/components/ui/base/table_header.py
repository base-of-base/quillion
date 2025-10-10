from typing import Optional, Callable
from ..element import Element


class TableHeader(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("th", *children, class_name=class_name, **kwargs)


def table_header(*children, **kwargs):
    return TableHeader(*children, **kwargs)
