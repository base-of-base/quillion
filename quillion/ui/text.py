from typing import Optional
from .element import Element


class Text(Element):
    def __init__(
        self,
        text: str,
        size: Optional[str] = None,
        color: Optional[str] = None,
        weight: Optional[str] = None,
        **kwargs
    ):
        super().__init__("p", text=text, **kwargs)


def text(text: str, **kwargs):
    return Text(text, **kwargs)
