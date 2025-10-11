from typing import Optional, Callable
from ..element import Element



class Emphasis(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("em", *children, class_name=class_name, **kwargs)

def emphasis(*children, **kwargs):
    return Emphasis(*children, **kwargs)
