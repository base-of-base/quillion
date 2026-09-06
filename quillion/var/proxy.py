"""Universal reactive proxy for any mutable object."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any


class ReactiveProxy:
    """
    Proxy that tracks mutations on lists, dicts, and their nested structures.
    Notifies on any change.
    """

    _target: Any
    _on_change: Callable[[], None]

    def __init__(self, target: Any, on_change: Callable[[], None]) -> None:
        self._target = target
        self._on_change = on_change

    def _wrap_value(self, value: Any) -> Any:
        """Wrap nested mutable collections in proxies."""
        if isinstance(value, (list, dict)):
            return ReactiveProxy(value, self._on_change)
        return value

    def __getattribute__(self, name: str) -> Any:
        """Intercept attribute access to wrap methods."""
        if name.startswith('_') or name in ('_target', '_on_change', '_wrap_value'):
            return super().__getattribute__(name)

        target = super().__getattribute__('_target')
        attr = getattr(target, name)

        if callable(attr) and name in ('append', 'extend', 'insert', 'remove', 'pop',
                                        'clear', 'sort', 'reverse', 'update',
                                        'setdefault', 'popitem'):
            on_change = super().__getattribute__('_on_change')
            def wrapped(*args: Any, **kwargs: Any) -> Any:
                result = attr(*args, **kwargs)
                on_change()
                return result
            return wrapped

        return attr

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('_') or name in ('_target', '_on_change'):
            super().__setattr__(name, value)
        else:
            old_value = getattr(self._target, name, None)
            setattr(self._target, name, value)
            if old_value != value:
                self._on_change()

    def __getitem__(self, key: Any) -> Any:
        """Return wrapped item for nested collections."""
        item = self._target[key]
        return self._wrap_value(item)

    def __setitem__(self, key: Any, value: Any) -> None:
        target = self._target
        old = target.get(key) if isinstance(target, dict) else target[key] if isinstance(target, list) and key < len(target) else None
        target[key] = value
        if old != value:
            self._on_change()

    def __delitem__(self, key: Any) -> None:
        """Delete item and notify."""
        del self._target[key]
        self._on_change()

    def __len__(self) -> int:
        return len(self._target)

    def __iter__(self) -> Iterator[Any]:
        """Iterate over wrapped items."""
        for item in self._target:
            yield self._wrap_value(item)

    def __contains__(self, item: Any) -> bool:
        return item in self._target

    def __repr__(self) -> str:
        return repr(self._target)

    def __str__(self) -> str:
        return str(self._target)
