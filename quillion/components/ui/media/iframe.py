from typing import Optional
from ..element import MediaElement


class Iframe(MediaElement):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("iframe", *children, class_name=class_name, **kwargs)


def iframe(*children, **kwargs):
    return Iframe(*children, **kwargs)
