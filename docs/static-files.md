# Static Files

Quillion can serve any static asset — images, fonts, CSS files, JavaScript — alongside your app.

---

## Registering a static directory

```python
from quillion import app

app.static("/static", "static/")
```

`app.static(url_prefix, directory)` mounts a local directory at a URL prefix. Any file inside `static/` will be served at `/static/<filename>`.

```
project/
├── app.py
└── static/
    ├── style.css
    ├── logo.png
    └── font.woff2
```

```python
# app.py
app.static("/static", "static/")
```

Now `http://localhost:8080/static/logo.png` serves the file.

---

## Multiple directories

You can mount as many directories as you need:

```python
app.static("/assets",  "assets/")
app.static("/uploads", "/var/data/user-uploads/")
app.static("/vendor",  "node_modules/dist/")
```

---

## Referencing static files from components

Use the URL prefix directly in props:

```python
from quillion import Image, Link, Script

Image("/static/logo.png", alt="Logo", height="40px")
Link("/static/style.css")
Script(src="/static/analytics.js")
```

---

## Global CSS from a file

Pass a file path to `app.css()` — quillion reads it and injects the contents:

```python
app.css("static/reset.css")
app.css("static/theme.css")
```

This differs from `app.static()`: the CSS is read once at startup and embedded in the WebSocket handshake, not served as a separate HTTP request. Use it for foundational styles; use `Link` for larger stylesheets or CDN resources.

---

## SPA fallback

For paths that are not static assets and have no matching `@page`, quillion serves `index.html` (the standard single-page app fallback). This is the file inside the `.q` directory that the quillion runtime places next to itself.

Files with a recognised extension (`.js`, `.css`, `.png`, etc.) are **never** served the SPA fallback — they return 404 instead if not found in a static directory. This prevents silently serving wrong content to browsers that expect a specific asset.

---

## Security

Quillion guards against directory traversal: a request for `/static/../../secret.txt` is rejected even if such a file exists on disk. The resolved path is checked to confirm it starts within the registered directory.
