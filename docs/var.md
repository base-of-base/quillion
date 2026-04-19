# Var — Reactive State

`Var` is the core primitive for state in quillion. It stores a single value and automatically updates every component that references it when the value changes.

---

## Creating a Var

```python
from quillion import var

name    = var("")          # string
count   = var(0)           # integer
active  = var(False)       # boolean
price   = var(9.99)        # float
```

Declare `Var`s at module level. Quillion detects their names automatically and uses them as stable keys — state survives hot reload.

---

## Reading and writing

Inside a page function or event handler, access `.value`:

```python
count = var(0)

@page("/")
def home():
    print(count.value)   # read
    count.value = 10     # write — triggers update
    ...
```

`Var` is **session-scoped**: each browser tab has its own independent copy of every value. Module-level `Var` objects are shared structure, not shared data.

---

## Using Var in components

Pass a `Var` directly where text content is expected. The component re-renders automatically when the value changes:

```python
from quillion import var, Container, Text, Button

score = var(0)

@page("/")
def home():
    return Container(
        Text("Score: ", score),       # re-renders on change
        Button("+10", on_click=lambda: score + 10),
    )
```

`Text`, `Heading`, and `Span` all accept a mix of plain strings and `Var` objects in their `*parts` argument.

---

## Arithmetic operators

`Var` supports `+` and `-` as shorthand for in-place mutation:

```python
count + 1     # equivalent to: count.value += 1
count - 1     # equivalent to: count.value -= 1
```

This makes `on_click` lambdas concise:

```python
Button("increment", on_click=lambda: count + 1)
```

---

## Two-way binding with input fields

Bind a `Var` to an `InputComponent` so it stays in sync in both directions — user typing updates the `Var`, and programmatic writes update the input:

```python
from quillion import var, Container, Text
from quillion import InputComponent

username = var("")

@page("/")
def home():
    return Container(
        username(),              # renders a bound <input>
        Text("Hello, ", username),
    )
```

Calling a `Var` as a function — `username()` — creates the default two-way component (which is `InputComponent` unless you change it). You can also be explicit:

```python
username(as_component="input")              # by alias
username(as_component=InputComponent)       # by class
username(placeholder="Enter your name…")   # with extra props
```

---

## Custom binding factory

If you want a `Var` to always render as a specific component, attach a factory:

```python
from quillion import var
from mycomponents import Slider

volume = var(50).bind_with(lambda **kw: Slider(bind_var=volume, **kw))

@page("/")
def home():
    return volume()   # renders Slider, not InputComponent
```

---

## Observing changes

You can run arbitrary code whenever a `Var` changes by calling `.observe()` on it. This is how `Text` and two-way components work internally:

```python
count = var(0)

def on_change(component, v, session):
    print(f"count changed to {v.value}")

count.observe(some_component, on_change)
```

The observer is called with `(component, var, session)` after every `.value` write. Observers are held in a `WeakKeyDictionary`, so they don't prevent garbage collection.

---

## Stable keys and hot reload

Quillion assigns each `Var` a UUID at creation time. On first load it also records the Python variable name → UUID mapping. When you hot-reload your file, new `Var` objects are created, but quillion looks up the original UUID by name and reuses it — so browser sessions keep their state across reloads.

If you create `Var`s dynamically (inside functions), pass `name` explicitly to opt into stable key behaviour:

```python
v = var(0, name="my_counter")
```

---

## Type coercion

When the initial value is typed, quillion coerces incoming event strings automatically:

| initial type | `"42"` becomes | `""` becomes |
|---|---|---|
| `int` | `42` | `0` |
| `float` | `42.0` | `0.0` |
| `bool` | `False` | `False` |
| `str` | `"42"` | `""` |

---

## Common patterns

**Derived display value**

```python
celsius = var(0)

@page("/")
def home():
    f = celsius.value * 9 / 5 + 32
    return Container(
        celsius(),
        Text(f"= {f:.1f} °F"),
    )
```

**Toggling a boolean**

```python
dark = var(False)

@page("/")
def home():
    return Container(
        Button("toggle theme", on_click=lambda: setattr(dark, 'value', not dark.value)),
    )
```

**Resetting state**

```python
count = var(0)

@page("/")
def home():
    return Container(
        Text(count),
        Button("reset", on_click=lambda: setattr(count, 'value', 0)),
    )
```
