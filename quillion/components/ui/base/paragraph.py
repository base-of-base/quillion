from typing import Optional, Callable
from ..element import Element


class Paragraph(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("p", *children, class_name=class_name, **kwargs)


def paragraph(*children, **kwargs):
    return Paragraph(*children, **kwargs)
