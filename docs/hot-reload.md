# Hot Reload

The quillion dev server watches your file for changes and updates every open browser tab without a full page reload — state is preserved where possible.

---

## How it works

When you run:

```
quillion run app.py
```

Quillion starts a background task that polls `app.py` every 300 ms using an MD5 hash. When the hash changes, it:

1. Reloads the module with `importlib.reload`.
2. Re-runs `auto_name_vars` to re-link `Var` names to stable UUIDs.
3. Calls `session.hot_reload()` on every connected browser session.
4. Each session re-calls the current page function and sends the new component tree.

The browser replaces the entire tree. In-flight state (values stored in `Var`s) is preserved because `Var` values live in the session, not the component objects.

---

## Terminal output

```
  [q]  quillion

  local    http://localhost:8080
  ws       ws://localhost:8765

  ready in 42ms  press q to quit

  ~  app.py  18.3ms
  +  2 clients
```

| symbol | meaning |
|---|---|
| `~` | Reload triggered, module loaded successfully |
| `+` | N browser sessions updated |
| `x` | Module raised an exception during reload |

---

## State preservation

`Var` values survive hot reload because they are keyed by stable UUIDs that are recorded by variable name at first load. Adding, removing, or renaming a `Var` in your code changes which UUID maps to which name, but existing session state for unchanged names is preserved.

Component event handler registrations are **not** preserved — each reload issues fresh IDs for all event listeners. This is intentional: stale handler closures from the old module are discarded.

---

## Error handling

If your file has a syntax error or raises an exception during reload:

```
  x  SyntaxError: invalid syntax (app.py, line 42)  5.1ms
```

The connected browser sessions are not touched — they continue showing the last good render. Fix the error and save; the next successful reload will update the browser.

---

## Reloading multiple files

The watcher only tracks the single file passed to `q run`. If you split your app across multiple files, changes to imported modules will not trigger a reload automatically.

**Workaround:** touch your main file after saving a dependency:

```bash
# save components/card.py, then:
touch app.py
```

Or use a filesystem watcher like `watchmedo` to automate this during development.

---

## Disabling the watcher

Hot reload is only active when you launch via `quillion run`. If you call `app.run()` directly from Python without passing a `watch` argument, no file watcher is started:

```python
app.run(host="0.0.0.0", port=8765, http_port=8080)
# no watch= → no watcher
```

This is the intended behaviour for production use.
