from .element import Element


class Text(Element):
    def __init__(self, text: str, **kwargs):
        super().__init__("p", text=text, **kwargs)
