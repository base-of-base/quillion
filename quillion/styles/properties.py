from typing import Dict, Optional, List
import webcolors

# --- Карты для сопоставления сокращенных значений с реальными CSS ---
COLOR_MAP = {
    "green": "#48bb78",
    "gray-100": "#f7fafc",
    "gray-600": "#718096",
    "white": "#ffffff",
}

BORDER_RADIUS_MAP = {
    "lg": "0.5rem",
    "md": "0.375rem",
    "sm": "0.25rem",
}

BOX_SHADOW_MAP = {
    "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
    "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
}

FONT_SIZE_MAP = {
    "2xl": "1.5rem",
    "3xl": "1.875rem",
}

FONT_WEIGHT_MAP = {
    "bold": "700",
    "normal": "400",
}


# --- Вспомогательная функция для добавления 'px' к числовым значениям ---
def _add_px_unit(value):
    """Добавляет 'px', если значение является числом или строкой с числом."""
    if isinstance(value, (int, float)) or (isinstance(value, str) and value.isdigit()):
        return f"{value}px"
    return value


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
            props["background-color"] = webcolors.name_to_hex(self.color)
        if self.image:
            props["background-image"] = f"url('{self.image.src}')"
        return props


class Color:
    def __init__(self, value: str):
        # Используем карту цветов или возвращаем исходное значение
        self.hex = COLOR_MAP.get(value, value)


class Image:
    def __init__(self, src: str):
        self.src = src


class Padding(StyleProperty):
    def __init__(self, value: str):
        self.value = value

    def to_css_properties_dict(self) -> Dict[str, str]:
        return {"padding": _add_px_unit(self.value)}


class Margin(StyleProperty):
    def __init__(self, value: str):
        self.value = value

    def to_css_properties_dict(self) -> Dict[str, str]:
        return {"margin": _add_px_unit(self.value)}


class DisplayFlex(StyleProperty):
    def __init__(
        self,
        direction: str = "row",
        justify: str = "flex-start",
        align: str = "stretch",
        gap=0,
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
            "gap": _add_px_unit(self.gap),
        }


class BorderRadius(StyleProperty):
    def __init__(self, value: str):
        self.value = value

    def to_css_properties_dict(self) -> Dict[str, str]:
        # Используем карту border-radius или возвращаем исходное значение
        val = BORDER_RADIUS_MAP.get(self.value, self.value)
        return {"border-radius": val}


class BoxShadow(StyleProperty):
    def __init__(self, value: str):
        self.value = value

    def to_css_properties_dict(self) -> Dict[str, str]:
        # Используем карту box-shadow или возвращаем исходное значение
        val = BOX_SHADOW_MAP.get(self.value, self.value)
        return {"box-shadow": val}


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
        # Используем карту font-size или возвращаем исходное значение
        val = FONT_SIZE_MAP.get(self.value, self.value)
        return {"font-size": val}


class FontWeight(StyleProperty):
    def __init__(self, value: str):
        self.value = value

    def to_css_properties_dict(self) -> Dict[str, str]:
        # Используем карту font-weight или возвращаем исходное значение
        val = FONT_WEIGHT_MAP.get(self.value, self.value)
        return {"font-weight": val}


class Width(StyleProperty):
    def __init__(self, value: str):
        self.value = value

    def to_css_properties_dict(self) -> Dict[str, str]:
        return {"width": _add_px_unit(self.value)}


class MinHeight(StyleProperty):
    def __init__(self, value: str):
        self.value = value

    def to_css_properties_dict(self) -> Dict[str, str]:
        return {"min-height": _add_px_unit(self.value)}


class TextDecoration(StyleProperty):
    def __init__(self, value: str):
        self.value = value

    def to_css_properties_dict(self) -> Dict[str, str]:
        return {"text-decoration": self.value}


class TextColor(StyleProperty):
    def __init__(self, value: str):
        self.value = value

    def to_css_properties_dict(self) -> Dict[str, str]:
        # Используем карту цветов или возвращаем исходное значение
        val = COLOR_MAP.get(self.value, self.value)
        return {"color": val}


class BorderColor(StyleProperty):
    def __init__(self, color: str):
        self.color = color

    def to_css_properties_dict(self) -> Dict[str, str]:
        # Используем карту цветов или возвращаем исходное значение
        val = COLOR_MAP.get(self.color, self.color)
        return {"border-color": val}


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
