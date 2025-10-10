from typing import Optional
from ..element import MediaElement


class Picture(MediaElement):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("picture", *children, class_name=class_name, **kwargs)


def picture(*children, **kwargs):
    return Picture(*children, **kwargs)
