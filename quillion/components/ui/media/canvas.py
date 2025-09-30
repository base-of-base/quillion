from typing import Optional
from ..element import MediaElement


class Canvas(MediaElement):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("canvas", *children, class_name=class_name, **kwargs)


def canvas(*children, **kwargs):
    return Canvas(*children, **kwargs)
