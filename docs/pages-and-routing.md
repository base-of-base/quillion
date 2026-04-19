# Pages & Routing

Quillion has a simple client-side router. Pages are plain Python functions decorated with `@page`.

---

## Defining a page

```python
from quillion import app, page, Container, Heading

@page("/")
def home():
    return Container(
        Heading("Home", level=1),
    )
```

`@page(path)` is a decorator that registers the function as the handler for that URL path. The function must return a single root `Component`.

`page` is a shorthand for `app.page` — both are identical:

```python
@app.page("/about")
def about():
    ...
```

---

## Multiple pages

Register as many pages as you need. Each is a separate function:

```python
from quillion import app, page, Container, Heading, NavLink

@page("/")
def home():
    return Container(
        nav(),
        Heading("Home", level=1),
    )

@page("/about")
def about():
    return Container(
        nav(),
        Heading("About", level=1),
    )

def nav():
    return Container(
        NavLink("/", "Home"),
        NavLink("/about", "About"),
        display="flex",
        gap="1rem",
    )
```

Pages can share helper functions freely — they are just Python.

---

## Navigation

### NavLink

`NavLink` renders an `<a>` tag that navigates without a full page reload. It sends a `navigate` message over the WebSocket; the server calls the new page function and sends back the component tree.

```python
from quillion import NavLink

NavLink("/about", "About us")
NavLink("/", "← Back")
```

Props:

| prop | type | description |
|---|---|---|
| `path` | `str` | Target URL path |
| `label` | `str` | Link text |

### Programmatic navigation

Navigate from an event handler by calling the session navigator directly:

```python
import asyncio
from quillion import app, page, Button, Container
from quillion._context import current_session

@page("/")
def home():
    def go_to_about():
        session = current_session.get()
        if session:
            asyncio.create_task(
                session.navigator.navigate_to("/about", session.serializer)
            )

    return Container(
        Button("Go to About", on_click=go_to_about),
    )
```

---

## Page state

Each browser session has isolated state. A `Var` defined at module level holds a separate value per session:

```python
from quillion import var, page, Container, Text, Button

step = var(0)

@page("/step-1")
def step1():
    return Container(
        Text("Step 1"),
        Button("Next →", on_click=lambda: ...),
    )
```

Two tabs open simultaneously each get their own `step` value.

---

## Splitting pages across files

For larger apps, organise pages in separate modules and import them before calling `app.run()`:

```
app.py
pages/
  home.py
  about.py
  dashboard.py
```

```python
# app.py
from quillion import app

import pages.home
import pages.about
import pages.dashboard

app.run()
```

```python
# pages/home.py
from quilling import page, Container, Heading

@page("/")
def home():
    return Container(Heading("Home", level=1))
```

Importing the module is enough — `@page` registers the route as a side effect.

---

## Route matching

Quillion does exact path matching. There is currently no wildcard or parameterised routing. The router checks `path in app.routes` and falls back to `"/"` if the path is not found.

---

## 404 behaviour

If the browser navigates to an unregistered path, quillion serves the SPA `index.html` (standard single-page app behaviour). The client then sends a `navigate` message; if no route matches, the server does nothing and the browser stays on the previous tree.
