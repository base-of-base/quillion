from typing import Optional, Callable
from ..element import Element


class Template(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("template", *children, class_name=class_name, **kwargs)


def template(*children, **kwargs):
    return Template(*children, **kwargs)
