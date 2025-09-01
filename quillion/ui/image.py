from typing import Optional
from .element import Element
from ..styles.properties import Width


class Image(Element):
    def __init__(self, src: str, width: Optional[int] = None, **kwargs):
        super().__init__("img", **kwargs)
        self.attributes["src"] = src
        if width:
            self.style_properties.append(Width(str(width)))


def image(src: str, **kwargs):
    return Image(src, **kwargs)
