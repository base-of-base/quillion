# Custom Components

You can create reusable components by subclassing `Component` or `TwoWayBindingElement`. This is the primary way to encapsulate UI logic in quillion.

---

## Function components

The simplest approach — a plain Python function that returns a component tree:

```python
from quillion import Container, Text, Heading

def Card(title: str, body: str):
    return Container(
        Heading(title, level=3, margin="0 0 0.5rem 0"),
        Text(body, color="#555"),
        background="#fff",
        border_radius="8px",
        padding="1.25rem",
        box_shadow="0 1px 4px rgba(0,0,0,.1)",
    )

# usage
@page("/")
def home():
    return Container(
        Card("Revenue", "$12,400"),
        Card("Users",   "1,023"),
        display="flex",
        gap="1rem",
    )
```

Function components are the idiomatic choice for most situations.

---

## Class components

Subclass `Component` when you need fine-grained control over props, children, or serialization:

```python
from quilling.components.base import Component
from typing import Any, Dict, List

class Badge(Component):
    tag_name = "span"

    def __init__(self, label: str, variant: str = "default", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.label   = label
        self.variant = variant

    def get_props(self) -> Dict[str, Any]:
        colours = {
            "default": ("#eee", "#333"),
            "success": ("#d1fae5", "#065f46"),
            "danger":  ("#fee2e2", "#991b1b"),
        }
        bg, fg = colours.get(self.variant, colours["default"])
        props = {
            "textContent": self.label,
            "style": f"background:{bg};color:{fg};border-radius:999px;padding:2px 10px;font-size:.8rem",
        }
        props.update(super().get_props())
        return props
```

```python
Badge("active",  variant="success")
Badge("deleted", variant="danger")
```

### Key methods to override

| method | purpose |
|---|---|
| `get_props()` | Return the dict of HTML attributes / props sent to the browser. Always call `super().get_props()` and merge. |
| `get_children()` | Return the list of child components. Default returns `self.children`. |
| `_post_init()` | Called by the metaclass after `__init__`. Use for observer setup. |

---

## Components with event handlers

Define methods named `on_<event>` to handle DOM events:

```python
from quillion.components.base import Component
from quillion import var
from typing import Any, Dict, Optional

clicks = var(0)

class CountingButton(Component):
    tag_name = "button"

    def __init__(self, label: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.label = label

    def get_props(self) -> Dict[str, Any]:
        props = {"textContent": self.label}
        props.update(super().get_props())
        return props

    def on_click(self, event_data: Optional[Dict] = None) -> None:
        clicks + 1
```

Any method named `on_<event>` is automatically detected by `UIComponentMeta` and registered as an event handler. The method may accept zero arguments or one `event_data` dict argument.

---

## Two-way binding components

To create a component that syncs with a `Var`, subclass `TwoWayBindingElement`:

```python
from quillion.components.two_way import TwoWayBindingElement
from quillion.var import Var
from typing import Any, Dict, Optional

class Slider(TwoWayBindingElement):
    tag_name = "input"
    _component_alias = "slider"   # lets you do: my_var(as_component="slider")
    _is_default = False            # don't make this the default for all Vars

    def __init__(
        self,
        bind_var: Optional[Var] = None,
        min: int = 0,
        max: int = 100,
        **kwargs: Any,
    ) -> None:
        super().__init__(bind_var=bind_var, **kwargs)
        self.min = min
        self.max = max

    def get_props(self) -> Dict[str, Any]:
        props: Dict[str, Any] = {
            "type":  "range",
            "value": self.get_current_value(),
            "min":   str(self.min),
            "max":   str(self.max),
        }
        props.update(super().get_props())
        return props

    def on_input(self, event_data: Optional[Dict] = None) -> None:
        if event_data and "value" in event_data:
            self.update_var_from_event(event_data["value"])
```

```python
volume = var(50)

@page("/")
def home():
    return Container(
        volume(as_component="slider", min=0, max=100),
        Text("Volume: ", volume),
    )
```

### `TwoWayBindingElement` API

| method / attribute | purpose |
|---|---|
| `_component_alias` | String alias for use with `var(as_component=…)` |
| `_is_default` | If `True`, this class becomes the default component for all `Var()` calls |
| `get_current_value()` | Returns `str(self._bind_var.value)` or `""` |
| `update_var_from_event(value)` | Writes to the bound `Var`, coercing to the right type |

---

## Registering a default two-way component

If you want all `var()` calls to produce your component instead of `InputComponent`:

```python
from quillion import app
from mycomponents import MyInput

app.set_default_two_way_component(MyInput)
```

---

## Composing components

Components compose naturally:

```python
def FormField(label: str, v: var):
    return Container(
        Text(label, display="block", font_weight="600", margin_bottom="4px"),
        v(placeholder=label),
        margin_bottom="1rem",
    )

name  = var("")
email = var("")

@page("/")
def form():
    return Container(
        FormField("Name",  name),
        FormField("Email", email),
        Button("Submit", on_click=submit),
        max_width="400px",
        margin="2rem auto",
    )
```
