from typing import Optional
from ..element import MediaElement


class FigCaption(MediaElement):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("figcaption", *children, class_name=class_name, **kwargs)


def figcaption(*children, **kwargs):
    return FigCaption(*children, **kwargs)
