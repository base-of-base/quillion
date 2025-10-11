from typing import Optional, Callable
from ..element import Element


class Menu(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("menu", *children, class_name=class_name, **kwargs)


def menu(*children, **kwargs):
    return Menu(*children, **kwargs)
