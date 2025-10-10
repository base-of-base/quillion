from typing import Optional, Callable
from ..element import Element


class ListItem(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("li", *children, class_name=class_name, **kwargs)


def list_item(*children, **kwargs):
    return ListItem(*children, **kwargs)
