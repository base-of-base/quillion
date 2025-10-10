from typing import Optional
from ..element import MediaElement


class Audio(MediaElement):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("audio", *children, class_name=class_name, **kwargs)


def audio(*children, **kwargs):
    return Audio(*children, **kwargs)
