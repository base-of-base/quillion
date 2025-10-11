from typing import Optional, Callable
from ..element import Element


class Prompt(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("input", *children, class_name=class_name, **kwargs)


def prompt(*children, **kwargs):
    return Prompt(*children, **kwargs)
