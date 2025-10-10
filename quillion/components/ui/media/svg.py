from typing import Optional
from ..element import MediaElement


class Svg(MediaElement):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("svg", *children, class_name=class_name, **kwargs)


def svg(*children, **kwargs):
    return Svg(*children, **kwargs)
