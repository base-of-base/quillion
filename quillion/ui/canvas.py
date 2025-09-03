from .element import Element


class Canvas(Element):
    def __init__(self, **kwargs):
        super().__init__("canvas", **kwargs)

def canvas(*children, **kwargs):
    return Canvas(*children, **kwargs)
