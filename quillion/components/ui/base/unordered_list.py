from typing import Optional, Callable
from ..element import Element


class UnorderedList(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("ul", *children, class_name=class_name, **kwargs)


def unordered_list(*children, **kwargs):
    return UnorderedList(*children, **kwargs)
