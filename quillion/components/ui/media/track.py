from typing import Optional
from ..element import MediaElement


class Track(MediaElement):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("track", *children, class_name=class_name, **kwargs)


def track(*children, **kwargs):
    return Track(*children, **kwargs)
