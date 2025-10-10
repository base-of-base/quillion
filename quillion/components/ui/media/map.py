from typing import Optional
from ..element import MediaElement


class Map(MediaElement):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("map", *children, class_name=class_name, **kwargs)


def map(*children, **kwargs):
    return Map(*children, **kwargs)
