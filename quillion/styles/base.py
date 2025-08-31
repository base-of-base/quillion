from typing import List
from ..ui.container import Container


class StyleMeta(type):
    _global_styles_registry: List["Style"] = []

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if hasattr(cls, "is_global") and cls.is_global:
            cls._global_styles_registry.append(cls())


class Style(metaclass=StyleMeta):
    @property
    def is_global(self) -> bool:
        return False

    def styles(self) -> Container:
        return Container()
