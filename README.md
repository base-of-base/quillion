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

MIT
