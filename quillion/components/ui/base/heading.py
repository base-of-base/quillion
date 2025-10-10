from typing import Optional, Callable
from ..element import Element


class Heading(Element):
    def __init__(
        self, level: int, *children, class_name: Optional[str] = None, **kwargs
    ):
        if not 1 <= level <= 6:
            raise ValueError("Heading level must be between 1 and 6")
        super().__init__(f"h{level}", *children, class_name=class_name, **kwargs)


def heading(level: int, *children, **kwargs):
    return Heading(level, *children, **kwargs)
