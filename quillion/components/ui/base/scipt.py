from typing import Optional, Callable
from ..element import Element


class Script(Element):
    def __init__(
        self,
        *children,
        src: Optional[str] = None,
        class_name: Optional[str] = None,
        **kwargs
    ):
        super().__init__("script", *children, class_name=class_name, **kwargs)


def script(*children, **kwargs):
    return Script(*children, **kwargs)
