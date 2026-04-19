# Getting Started

## Installation

```
pip install quillion
```

Requires Python **3.11+** and the `websockets` package (installed automatically).

---

## Your first app

Create `app.py`:

```python
from quillion import app, page, var, Container, Heading, Text, Button

count = var(0)

@page("/")
def home():
    return Container(
        Heading("Counter", level=1),
        Text(count),
        Button("＋", on_click=lambda: count + 1),
        Button("－", on_click=lambda: count - 1),
        gap="1rem",
        display="flex",
        flex_direction="column",
        align_items="center",
        padding="2rem",
    )

app.run()
```

Start the dev server:

```
quillion run app.py
```

Open [http://localhost:8080](http://localhost:8080). The counter updates in real time without a page reload.

---

## How quillion works

```
browser ──── WebSocket ──── your Python server
   │                              │
   │  sends events (click, input) │
   │◄─────────────────────────────│ sends component tree diff
```

When you call `app.run()`, quillion starts two servers:

- **HTTP** (default `:8080`) — serves `index.html` and static assets.
- **WebSocket** (default `:8765`) — carries component trees and events.

Your page functions run entirely on the server. The browser receives a JSON tree and renders it; events come back as JSON messages. Only changed component props are sent on update, not the full tree.

---

## Project layout

A typical project looks like this:

```
myproject/
├── app.py          ← your pages and logic
├── components/     ← optional: custom components
│   └── card.py
└── static/         ← optional: CSS, fonts, images
    └── style.css
```

For larger apps you can split pages across multiple files and import them into `app.py`.

---

## CLI reference

```
quillion run <file>           start the dev server with hot reload
  --host    HOST              bind address (default: localhost)
  --port    PORT              WebSocket port (default: 8765)
  --http-port PORT            HTTP port (default: 8080)
```

You can also run as a module:

```
python -m quillion run app.py
```

---

## Next steps

- [Pages & Routing](pages-and-routing.md) — multiple pages and navigation
- [Var — Reactive State](var.md) — how state works
- [Components](components.md) — all built-in elements
