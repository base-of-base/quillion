from typing import Optional, Callable
from ..element import Element



class Strong(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("strong", *children, class_name=class_name, **kwargs)

def strong(*children, **kwargs):
    return Strong(*children, **kwargs)
