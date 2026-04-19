<h3 align="center">quillion</h3>
<p align="center">Build reactive web UIs in pure Python.</p>



<p align="center">
  <a href="https://pypi.org/project/quillion"><img src="https://img.shields.io/pypi/v/quillion?color=black&label=pypi" /></a>
  <a href="docs/"><img src="https://img.shields.io/badge/docs-→-black" /></a>
  <img src="https://img.shields.io/badge/python-3.11+-black" />
  <img src="https://img.shields.io/badge/license-MIT-black" />
</p>

---

```python
from quillion import app, page, var, container, text, button

count = var(0)

@page("/")
def index():
    return container(
        text(count),
        button("increment", on_click=lambda: count + 1),
    )

app.run()
```

```
q run app.py
```

---

## install

```
pip install quillion
```

Requires Python 3.11+ and a browser.

---

## how it works

Quillion runs a WebSocket server alongside a small HTTP server. Your page functions are called on the server — the resulting component tree is serialized and sent to the browser. Events (clicks, input changes) travel back over the socket, handlers run on the server, and only the changed nodes are patched in the DOM. No JavaScript, no templates, no build step.

---

## docs

| | |
|---|---|
| [Getting Started](docs/getting-started.md) | Install, first app, project layout |
| [Pages & Routing](docs/pages-and-routing.md) | `@page`, multi-page apps, navigation |
| [Var — Reactive State](docs/var.md) | How state works, observers, binding |
| [Components](docs/components.md) | Built-in elements, props, style, children |
| [Styling](docs/styling.md) | Inline styles, CSS classes, global CSS |
| [Static Files](docs/static-files.md) | Serving assets, custom directories |
| [Hot Reload](docs/hot-reload.md) | Dev workflow, file watcher |
| [Custom Components](docs/custom-components.md) | Subclassing Component and TwoWayBindingElement |

---

<p align="center"><sub>MIT © quillion contributors</sub></p>
