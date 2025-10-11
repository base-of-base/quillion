from typing import Optional, Callable
from ..element import Element



class Preformatted(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("pre", *children, class_name=class_name, **kwargs)

def preformatted(*children, **kwargs):
    return Preformatted(*children, **kwargs)
