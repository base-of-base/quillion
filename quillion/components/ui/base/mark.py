from typing import Optional, Callable
from ..element import Element



class Mark(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("mark", *children, class_name=class_name, **kwargs)

def mark(*children, **kwargs):
    return Mark(*children, **kwargs)
