from typing import Optional
from .element import Element


class Image(Element):
    def __init__(self, src: str, **kwargs):
        super().__init__("img", **kwargs)
        self.attributes["src"] = src


def image(src: str, **kwargs):
    return Image(src, **kwargs)
