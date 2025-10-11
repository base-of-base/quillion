from typing import Optional, Callable
from ..element import Element


class Summary(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("summary", *children, class_name=class_name, **kwargs)

def summary(*children, **kwargs):
    return Summary(*children, **kwargs)
