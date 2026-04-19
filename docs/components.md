# Components

Every element on the page is a `Component`. Quillion ships with a complete set of HTML element wrappers; you can also subclass `Component` to build your own.

---

## Anatomy of a component

```python
Button(
    "Click me",               # positional args → label / children / parts
    on_click=handle_click,    # event handler
    background="black",       # CSS property (camelCase or snake_case)
    color="white",
    padding="0.5rem 1rem",
    class_name="btn-primary", # HTML class attribute
)
```

- **Positional arguments** — component-specific (label, children, text parts).
- **`on_*` keyword arguments** — event handlers.
- **`class_name` / `className`** — sets the HTML `class` attribute.
- **Everything else** — treated as inline CSS (snake_case → kebab-case automatically).

---

## Built-in components

### Layout

#### `Container` / `Div`

A generic block wrapper (`<div>`).

```python
Container(
    child1,
    child2,
    display="flex",
    gap="1rem",
)
```

Positional args become children. Strings are automatically wrapped in `Text`.

#### `Span`

Inline wrapper (`<span>`).

```python
Span("hello", color="grey")
```

---

### Text

#### `Text`

Inline text node (`<span>`). Accepts a mix of strings and `Var`s; re-renders when any `Var` changes.

```python
Text("Hello, ", username, "!")
```

#### `Heading`

Renders `<h1>` through `<h6>`. Also reactive to `Var`s.

```python
Heading("Welcome", level=1)
Heading("Section", level=2)
Heading("Current score: ", score, level=3)
```

Props:

| prop | type | default | description |
|---|---|---|---|
| `*parts` | `str \| Var` | — | Text content |
| `level` | `int` | `1` | Heading level 1–6 |

---

### Interaction

#### `Button`

A `<button>` element.

```python
Button("Save", on_click=handle_save)
Button("Delete", on_click=lambda: count - 1, color="red")
```

Props:

| prop | type | description |
|---|---|---|
| `label` | `str` | Button text |
| `on_click` | `Callable` | Click handler (no args or one `event_data` arg) |

#### `InputComponent`

A `<input>` element with optional two-way `Var` binding. Usually created by calling a `Var`, not directly.

```python
# via Var (recommended)
username()
username(placeholder="Your name", type="email")

# directly
from quillion import InputComponent
InputComponent(bind_var=username, placeholder="…", type="text")
```

Props:

| prop | type | default | description |
|---|---|---|---|
| `bind_var` | `Var` | `None` | Var to sync with |
| `placeholder` | `str` | `""` | Placeholder text |
| `type` | `str` | `"text"` | HTML input type |

---

### Navigation

#### `NavLink`

Client-side navigation link (`<a>`). Does not trigger a full page reload.

```python
NavLink("/dashboard", "Dashboard")
```

#### `Anchor`

A plain `<a>` tag without routing behaviour.

```python
Anchor("Open docs", href="https://docs.example.com", rel="noopener")
```

Props:

| prop | type | default |
|---|---|---|
| `*children` | `Component \| str` | — |
| `href` | `str` | `"#"` |

---

### Media

#### `Image`

```python
Image("/static/logo.png", alt="Logo", width="120px")
```

Props:

| prop | type | default |
|---|---|---|
| `src` | `str` | required |
| `alt` | `str` | `""` |

---

### Head / meta

#### `Link`

A `<link>` tag, typically for stylesheets.

```python
Link("/static/style.css")
Link("/fonts/inter.css", rel="stylesheet")
```

#### `Script`

```python
Script(src="/static/analytics.js")
Script(content="console.log('loaded')")
```

#### `Style`

Inline `<style>` block.

```python
Style("body { margin: 0; font-family: sans-serif; }")
```

---

### Lists

```python
UnorderedList(
    ListItem("First"),
    ListItem("Second"),
    ListItem(Text("With a ", Span("nested span"))),
)

OrderedList(
    ListItem("Step one"),
    ListItem("Step two"),
)
```

Aliases: `ul`, `ol`, `li`.

---

### Utility

```python
Break()           # <br>
HorizontalRule()  # <hr>
```

---

## Children

Any component that accepts `*children` will wrap bare strings in `Text` automatically:

```python
Container("hello", "world")
# is equivalent to:
Container(Text("hello"), Text("world"))
```

---

## CSS props

All keyword arguments that are not recognised as component-specific props or event handlers are treated as CSS properties and collected into an inline `style` attribute. snake_case is converted to kebab-case:

```python
Container(
    flex_direction="row",   # → flex-direction: row
    backgroundColor="red",  # → background-color: red (camelCase also works)
    padding="1rem",
)
```

---

## Lowercase aliases

Every component has a lowercase alias for compact code:

```python
from quillion import container, text, button, heading, div, span
from quillion import navlink, image, link, script, style
from quillion import ul, ol, li, a, br, hr
```

---

## Component IDs

Each component instance receives a short random `_id` (8 hex characters) at creation time. The browser uses this ID to locate nodes for in-place prop updates. IDs are not stable across re-renders — if you need stable references, use `Var` observers.
