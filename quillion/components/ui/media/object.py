from typing import Optional
from ..element import MediaElement


class Object(MediaElement):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("object", *children, class_name=class_name, **kwargs)


def object(*children, **kwargs):
    return Object(*children, **kwargs)
