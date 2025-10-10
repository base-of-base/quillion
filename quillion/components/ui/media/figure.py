from typing import Optional
from ..element import MediaElement


class Figure(MediaElement):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("figure", *children, class_name=class_name, **kwargs)


def figure(*children, **kwargs):
    return Figure(*children, **kwargs)
