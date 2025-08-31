from typing import Optional, Callable
from .element import Element


class Button(Element):
    def __init__(self, text: str, on_click: Optional[Callable] = None, **kwargs):
        super().__init__("button", text=text, on_click=on_click, **kwargs)
