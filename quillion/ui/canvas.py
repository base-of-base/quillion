from .element import Element


class Canvas(Element):
    def __init__(self, width: int = 300, height: int = 150, **kwargs):
        super().__init__("canvas", **kwargs)
        self.attributes["width"] = str(width)
        self.attributes["height"] = str(height)
