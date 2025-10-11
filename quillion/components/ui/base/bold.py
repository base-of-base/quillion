from typing import Optional, Callable
from ..element import Element



class Bold(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("b", *children, class_name=class_name, **kwargs)

def bold(*children, **kwargs):
    return Bold(*children, **kwargs)
