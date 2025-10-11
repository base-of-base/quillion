from typing import Optional, Callable
from ..element import Element



class Underline(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("u", *children, class_name=class_name, **kwargs)

def underline(*children, **kwargs):
    return Underline(*children, **kwargs)
