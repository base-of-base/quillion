"""
Quillion — a lightweight reactive UI framework for Python.
"""

from .app import App, app, page
from .var import Var, var
from .components.base import Component
from .components.two_way import TwoWayBindingElement
from .components.elements import (
    Container, Text, Button, Heading, Div, Span,
    NavLink, Image, Link, Script, Style,
    UnorderedList, OrderedList, ListItem, Anchor, Break, HorizontalRule,
    # lowercase aliases
    container, text, button, heading, div, span,
    navlink, image, link, script, style,
    ul, ol, li, a, br, hr,
)
from .components.input import InputComponent

__all__ = [
    "App", "app", "page",
    "Var", "var",
    "Component", "TwoWayBindingElement",
    "Container", "Text", "Button", "Heading", "Div", "Span",
    "NavLink", "Image", "Link", "Script", "Style",
    "UnorderedList", "OrderedList", "ListItem", "Anchor", "Break", "HorizontalRule",
    "InputComponent",
    "container", "text", "button", "heading", "div", "span",
    "navlink", "image", "link", "script", "style",
    "ul", "ol", "li", "a", "br", "hr",
]
