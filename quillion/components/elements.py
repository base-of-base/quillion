"""
Concrete HTML element components.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from ..session import Session

from .. import _context as ctx
from .base import Component
from .mixins import ReactiveContainerMixin, TextMixin


def _wrap_children(children: Any) -> list[Component]:
    result: list[Component] = [Text(c) if isinstance(c, str) else c for c in children]
    return result


class Div(ReactiveContainerMixin, Component):
    tag_name = "div"

    def __init__(self, *children: Any, **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)


class Text(TextMixin, Component):
    tag_name = "span"


class Button(Component):
    tag_name = "button"

    def __init__(
        self, label: str, on_click: Callable[[Any], Any] | None = None, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.label = label
        self.on_click = on_click

    def get_props(self) -> dict[str, Any]:
        props: dict[str, Any] = {"textContent": self.label}
        props.update(super().get_props())
        return props


class Heading(TextMixin, Component):
    def __init__(self, *parts: Any, level: int = 1, **kwargs: Any) -> None:
        self.level = min(max(level, 1), 6)
        self.tag_name = f"h{self.level}"
        super().__init__(*parts, **kwargs)


class Span(ReactiveContainerMixin, Text):
    tag_name = "span"


class NavLink(Component):
    tag_name = "a"

    def __init__(self, path: str, label: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.path = path
        self.label = label

    def get_props(self) -> dict[str, Any]:
        props: dict[str, Any] = {"textContent": self.label, "href": "#"}
        props.update(super().get_props())
        return props

    def on_click(self, event_data: dict | None = None) -> None:
        session = cast("Session", ctx.current_session.get())
        if session:
            asyncio.create_task(
                session.navigator.navigate_to(self.path, session.serializer)
            )


class Image(Component):
    tag_name = "img"

    def __init__(self, src: str, alt: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.src = src
        self.alt = alt

    def get_props(self) -> dict[str, Any]:
        props: dict[str, Any] = {"src": self.src, "alt": self.alt}
        props.update(super().get_props())
        return props


class Link(Component):
    tag_name = "link"

    def __init__(self, href: str, rel: str = "stylesheet", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.href = href
        self.rel = rel

    def get_props(self) -> dict[str, Any]:
        props: dict[str, Any] = {"href": self.href, "rel": self.rel}
        props.update(super().get_props())
        return props


class Script(Component):
    tag_name = "script"

    def __init__(
        self, src: str | None = None, content: str | None = None, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.src = src
        self.content = content

    def get_props(self) -> dict[str, Any]:
        props: dict[str, Any] = {}
        if self.src:
            props["src"] = self.src
        if self.content:
            props["textContent"] = self.content
        props.update(super().get_props())
        return props

    def get_children(self) -> list[Component]:
        return []


class Style(Component):
    tag_name = "style"

    def __init__(self, content: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.content = content

    def get_props(self) -> dict[str, Any]:
        props: dict[str, Any] = {"textContent": self.content}
        props.update(super().get_props())
        return props

    def get_children(self) -> list[Component]:
        return []


class UnorderedList(Component):
    tag_name = "ul"

    def __init__(self, *children: Any, **kwargs: Any) -> None:
        self.children = _wrap_children(children)
        super().__init__(**kwargs)


class OrderedList(Component):
    tag_name = "ol"

    def __init__(self, *children: Any, **kwargs: Any) -> None:
        self.children = _wrap_children(children)
        super().__init__(**kwargs)


class ListItem(Component):
    tag_name = "li"

    def __init__(self, *children: Any, **kwargs: Any) -> None:
        self.children = _wrap_children(children)
        super().__init__(**kwargs)


class Anchor(Component):
    tag_name = "a"

    def __init__(self, *children: Any, href: str = "#", **kwargs: Any) -> None:
        self.href = href
        self.children = _wrap_children(children)
        super().__init__(**kwargs)

    def get_props(self) -> dict[str, Any]:
        props: dict[str, Any] = {"href": self.href}
        props.update(super().get_props())
        return props


class Break(Component):
    tag_name = "br"

    def get_children(self) -> list[Component]:
        return []


class HorizontalRule(Component):
    tag_name = "hr"

    def get_children(self) -> list[Component]:
        return []


text: type[Text] = Text
button: type[Button] = Button
heading: type[Heading] = Heading
div: type[Div] = Div
span: type[Span] = Span
navlink: type[NavLink] = NavLink
image: type[Image] = Image
link: type[Link] = Link
script: type[Script] = Script
style: type[Style] = Style
ul: type[UnorderedList] = UnorderedList
ol: type[OrderedList] = OrderedList
li: type[ListItem] = ListItem
a: type[Anchor] = Anchor
br: type[Break] = Break
hr: type[HorizontalRule] = HorizontalRule
