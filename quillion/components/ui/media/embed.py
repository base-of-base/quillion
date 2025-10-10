from typing import Optional
from ..element import MediaElement


class Embed(MediaElement):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("embed", *children, class_name=class_name, **kwargs)


def embed(*children, **kwargs):
    return Embed(*children, **kwargs)
