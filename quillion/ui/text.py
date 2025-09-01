from typing import Optional
from .element import Element
from ..styles.properties import FontSize, TextColor, FontWeight

class Text(Element):
    def __init__(self, text: str, size: Optional[str] = None, color: Optional[str] = None, weight: Optional[str] = None, **kwargs):
        super().__init__("p", text=text, **kwargs)
        if size:
            self.style_properties.append(FontSize(size))
        if color:
            self.style_properties.append(TextColor(color))
        if weight:
            self.style_properties.append(FontWeight(weight))

def text(text: str, **kwargs):
    return Text(text, **kwargs)