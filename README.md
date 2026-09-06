<h3 align="center">quillion</h3>
<p align="center">Build reactive web UIs in pure Python.</p>


<p align="center">
  <a href="https://pypi.org/project/quillion"><img src="https://img.shields.io/pypi/v/quillion?color=54cb8f&label=pypi" /></a>
  <a href="docs/"><img src="https://img.shields.io/badge/docs-→-54cb8f" /></a>
  <img src="https://img.shields.io/badge/python-3.11+-54cb8f" />
  <img src="https://img.shields.io/badge/license-MIT-54cb8f" />
</p>

---

```python
from quillion import app, page, var, container, text, button

count = 0

@page("/")
def index():
    return container(
        text(count),
        button("increment", on_click=lambda: count + 1),
    )

app.run()
```

#### And run it with:

```
q run app.py
```

---

## Install

```
pip install quillion
```

Requires Python 3.11+ and a browser.

---

[MIT](LICENSE)
