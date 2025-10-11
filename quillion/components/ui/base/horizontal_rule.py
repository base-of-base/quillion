from typing import Optional, Callable
from ..element import Element



class HorizontalRule(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("hr", *children, class_name=class_name, **kwargs)

def horizontal_rule(*children, **kwargs):
    return HorizontalRule(*children, **kwargs)
