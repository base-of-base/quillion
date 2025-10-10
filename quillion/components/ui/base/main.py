from typing import Optional, Callable
from ..element import Element


class Main(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("main", *children, class_name=class_name, **kwargs)


def main(*children, **kwargs):
    return Main(*children, **kwargs)
