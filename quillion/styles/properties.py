from typing import Dict, Optional, List


class StyleProperty:
    def to_css_properties_dict(self) -> Dict[str, str]:
        raise NotImplementedError


class FontFamily(StyleProperty):
    def __init__(self, *fonts: str):
        self.fonts = fonts

    def to_css_properties_dict(self) -> Dict[str, str]:
        return {"font-family": ", ".join(self.fonts)}


class Background(StyleProperty):
    def __init__(
        self, color: Optional["Color"] = None, image: Optional["Image"] = None
    ):
        self.color = color
        self.image = image

    def to_css_properties_dict(self) -> Dict[str, str]:
        props = {}
        if self.color:
            props["background-color"] = self.color.hex
        if self.image:
            props["background-image"] = f"url('{self.image.src}')"
        return props


class Color:
    def __init__(self, hexcode: str):
        self.hex = hexcode


class Image:
    def __init__(self, src: str):
        self.src = src


class Padding(StyleProperty):
    def __init__(self, value: str):
        self.value = value

    def to_css_properties_dict(self) -> Dict[str, str]:
        return {"padding": self.value}


class Margin(StyleProperty):
    def __init__(self, value: str):
        self.value = value

    def to_css_properties_dict(self) -> Dict[str, str]:
        return {"margin": self.value}


class DisplayFlex(StyleProperty):
    def __init__(
        self,
        direction: str = "row",
        justify: str = "flex-start",
        align: str = "stretch",
        gap: int = 0,
    ):
        self.direction = direction
        self.justify = justify
        self.align = align
        self.gap = gap

    def to_css_properties_dict(self) -> Dict[str, str]:
        return {
            "display": "flex",
            "flex-direction": self.direction,
            "justify-content": self.justify,
            "align-items": self.align,
            "gap": f"{self.gap}px",
        }


class BorderRadius(StyleProperty):
    def __init__(self, value: str):
        self.value = value

    def to_css_properties_dict(self) -> Dict[str, str]:
        return {"border-radius": self.value}


class BoxShadow(StyleProperty):
    def __init__(self, value: str):
        self.value = value

    def to_css_properties_dict(self) -> Dict[str, str]:
        return {"box-shadow": self.value}


class Border(StyleProperty):
    def __init__(self, width: str, style: str, color: str):
        self.width = width
        self.style = style
        self.color = color

    def to_css_properties_dict(self) -> Dict[str, str]:
        return {"border": f"{self.width} {self.style} {self.color}"}


class Transition(StyleProperty):
    def __init__(self, value: str):
        self.value = value

    def to_css_properties_dict(self) -> Dict[str, str]:
        return {"transition": self.value}


class Cursor(StyleProperty):
    def __init__(self, value: str):
        self.value = value

    def to_css_properties_dict(self) -> Dict[str, str]:
        return {"cursor": self.value}


class FontSize(StyleProperty):
    def __init__(self, value: str):
        self.value = value

    def to_css_properties_dict(self) -> Dict[str, str]:
        return {"font-size": self.value}


class MinHeight(StyleProperty):
    def __init__(self, value: str):
        self.value = value

    def to_css_properties_dict(self) -> Dict[str, str]:
        return {"min-height": self.value}


class TextDecoration(StyleProperty):
    def __init__(self, value: str):
        self.value = value

    def to_css_properties_dict(self) -> Dict[str, str]:
        return {"text-decoration": self.value}


class TextColor(StyleProperty):
    def __init__(self, hexcode: str):
        self.hex = hexcode

    def to_css_properties_dict(self) -> Dict[str, str]:
        return {"color": self.hex}


class BorderColor(StyleProperty):
    def __init__(self, color: str):
        self.color = color

    def to_css_properties_dict(self) -> Dict[str, str]:
        return {"border-color": self.color}


class LineHeight(StyleProperty):
    def __init__(self, value: float):
        self.value = value

    def to_css_properties_dict(self) -> Dict[str, str]:
        return {"line-height": str(self.value)}


class ParagraphBase(StyleProperty):
    def __init__(self, *properties: StyleProperty):
        self.properties = properties

    def to_css_properties_dict(self) -> Dict[str, str]:
        props = {}
        for prop in self.properties:
            if prop:
                props.update(prop.to_css_properties_dict())
        return props


class ButtonBase(StyleProperty):
    def __init__(self, *properties: StyleProperty):
        self.properties = properties

    def to_css_properties_dict(self) -> Dict[str, str]:
        props = {}
        for prop in self.properties:
            if prop:
                props.update(prop.to_css_properties_dict())
        return props


class ButtonHover(StyleProperty):
    def __init__(self, *properties: StyleProperty):
        self.properties = properties

    def to_css_properties_dict(self) -> Dict[str, str]:
        props = {}
        for prop in self.properties:
            if prop:
                props.update(prop.to_css_properties_dict())
        return props


class LinkBase(StyleProperty):
    def __init__(self, *properties: StyleProperty):
        self.properties = properties

    def to_css_properties_dict(self) -> Dict[str, str]:
        props = {}
        for prop in self.properties:
            if prop:
                props.update(prop.to_css_properties_dict())
        return props


class LinkHover(StyleProperty):
    def __init__(self, *properties: StyleProperty):
        self.properties = properties

    def to_css_properties_dict(self) -> Dict[str, str]:
        props = {}
        for prop in self.properties:
            if prop:
                props.update(prop.to_css_properties_dict())
        return props
