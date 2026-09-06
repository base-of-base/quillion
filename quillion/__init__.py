"""
Quillion — a lightweight reactive UI framework for Python.
"""

from .app import App, app, page
from .var import Var, auto_name_vars

__all__ = [
    "Anchor",
    "App",
    "Break",
    "Button",
    "Component",
    "Div",
    "Heading",
    "HorizontalRule",
    "Image",
    "InputComponent",
    "Link",
    "ListItem",
    "NavLink",
    "OrderedList",
    "Script",
    "Span",
    "Style",
    "Text",
    "TwoWayBindingElement",
    "UnorderedList",
    "Var",
    "a",
    "app",
    "auto_name_vars",
    "br",
    "button",
    "div",
    "heading",
    "hr",
    "image",
    "input",
    "li",
    "link",
    "navlink",
    "ol",
    "page",
    "script",
    "span",
    "style",
    "text",
    "ul",
    "var"
]


def __getattr__(name: str):
    if name in __all__:
        from .components.base import Component
        from .components.elements import (
            Anchor,
            Break,
            Button,
            Div,
            Heading,
            HorizontalRule,
            Image,
            Link,
            ListItem,
            NavLink,
            OrderedList,
            Script,
            Span,
            Style,
            Text,
            UnorderedList,
            a,
            br,
            button,
            div,
            heading,
            hr,
            image,
            li,
            link,
            navlink,
            ol,
            script,
            span,
            style,
            text,
            ul,
        )
        from .components.input import InputComponent, input
        from .components.two_way import TwoWayBindingElement
        from .var import VarNamespace
        ctx_vars = {
            "Component": Component, "Anchor": Anchor, "Break": Break,
            "Button": Button, "Div": Div, "Heading": Heading,
            "HorizontalRule": HorizontalRule, "Image": Image,
            "InputComponent": InputComponent, "Link": Link,
            "ListItem": ListItem, "NavLink": NavLink,
            "OrderedList": OrderedList, "Script": Script, "Span": Span,
            "Style": Style, "Text": Text, "TwoWayBindingElement": TwoWayBindingElement,
            "UnorderedList": UnorderedList, "Var": Var,
            "a": a, "app": app, "auto_name_vars": auto_name_vars,
            "br": br, "button": button, "div": div, "heading": heading,
            "hr": hr, "image": image, "input": input, "li": li,
            "link": link, "navlink": navlink, "ol": ol, "page": page,
            "script": script, "span": span, "style": style,
            "text": text, "ul": ul, "var": VarNamespace(),
        }
        if name in ctx_vars:
            return ctx_vars[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
