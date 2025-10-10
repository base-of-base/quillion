from typing import Optional
from ..element import MediaElement


class Area(MediaElement):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("area", *children, class_name=class_name, **kwargs)


def area(*children, **kwargs):
    return Area(*children, **kwargs)
