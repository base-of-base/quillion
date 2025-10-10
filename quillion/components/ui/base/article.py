from typing import Optional, Callable
from ..element import Element


class Article(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("article", *children, class_name=class_name, **kwargs)


def article(*children, **kwargs):
    return Article(*children, **kwargs)
