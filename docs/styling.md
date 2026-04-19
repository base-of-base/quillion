# Styling

Quillion gives you three layers of styling: inline CSS props, class names, and global CSS. They compose freely.

---

## Inline styles

Pass CSS properties as keyword arguments. snake_case is converted to kebab-case automatically.

```python
Container(
    padding="2rem",
    display="flex",
    flex_direction="column",
    align_items="center",
    background_color="#f5f5f5",
    border_radius="8px",
    gap="1rem",
)
```

camelCase also works:

```python
Container(borderRadius="8px", backgroundColor="#fff")
```

Under the hood this becomes `style="border-radius: 8px; background-color: #fff"` on the DOM node.

---

## Class names

Pass `class_name` (or `className`) to add an HTML `class` attribute:

```python
Button("Primary", class_name="btn btn-primary", on_click=handle)
Container(child, class_name="card elevated")
```

This lets you use an external stylesheet, CSS framework, or CSS-in-JS approach alongside quillion.

---

## Global CSS

Inject CSS that applies across the whole page using `app.css()`:

```python
from quillion import app

# Inline string
app.css("""
  *, *::before, *::after { box-sizing: border-box; }
  body { margin: 0; font-family: system-ui, sans-serif; }
""")

# From a file
app.css("static/style.css")
```

`app.css()` can be called multiple times. All CSS strings are concatenated and sent to the browser as a single `<style>` block when a session connects.

```python
# Chaining is supported
app.css("static/reset.css").css("static/theme.css")
```

---

## Using a CSS framework

Serve the framework's CSS from your static directory and link it via `app.css()` or a `Link` component:

```python
from quillion import app, page, Container, Link, Heading

app.static("/static", "static/")

@page("/")
def home():
    return Container(
        Link("https://cdn.example.com/tailwind.css"),
        Heading("Hello", level=1, class_name="text-3xl font-bold"),
    )
```

---

## Style utilities pattern

For larger apps, define style dictionaries and spread them:

```python
card_style = dict(
    background="#fff",
    border_radius="12px",
    box_shadow="0 2px 8px rgba(0,0,0,.08)",
    padding="1.5rem",
)

def Card(*children):
    return Container(*children, **card_style)
```

---

## Dynamic styles

Because styles are computed at render time on the server, you can make them conditional with plain Python:

```python
active = var(False)

@page("/")
def home():
    bg = "#000" if active.value else "#eee"
    color = "#fff" if active.value else "#000"

    return Button(
        "Toggle",
        on_click=lambda: setattr(active, "value", not active.value),
        background=bg,
        color=color,
        transition="background 0.2s",
    )
```

The button re-renders with the new style whenever `active` changes.
