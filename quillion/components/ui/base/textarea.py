from typing import Optional, Callable
from ..element import Element


class TextArea(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("textarea", *children, class_name=class_name, **kwargs)


def textarea(*children, **kwargs):
    return TextArea(*children, **kwargs)
