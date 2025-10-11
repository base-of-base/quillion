from typing import Optional, Callable
from ..element import Element


class Dialog(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("dialog", *children, class_name=class_name, **kwargs)


def dialog(*children, **kwargs):
    return Dialog(*children, **kwargs)
