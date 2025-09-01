from .element import Element
from typing import List, Optional

class Container(Element):
    def __init__(self, *children, **kwargs):
        super().__init__("div", **kwargs)
        
        for child in children:
            self.append(child)

def box(*children, **kwargs):
    return Container(*children, **kwargs)