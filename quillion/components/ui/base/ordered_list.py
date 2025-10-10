from typing import Optional, Callable
from ..element import Element


class OrderedList(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("ol", *children, class_name=class_name, **kwargs)


def ordered_list(*children, **kwargs):
    return OrderedList(*children, **kwargs)
