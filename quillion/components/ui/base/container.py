from ..element import Element
from typing import List, Optional


class Container(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("div", class_name=class_name, **kwargs)

        for child in children:
            self.append(child)


def container(*children, **kwargs):
    return Container(*children, **kwargs)
