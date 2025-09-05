import asyncio
import inspect
from typing import Optional, Any, Callable
from pydantic import BaseModel, ValidationError


class StateMeta(type):
    def __init__(self, name, bases, attrs):
        super().__init__(name, bases, attrs)
        self._defaults = {}

        for key in list(attrs.keys()):
            if not key.startswith("_") and not (
                callable(attrs[key])
                or isinstance(attrs[key], (classmethod, staticmethod, property))
            ):
                self._defaults[key] = attrs[key]

        if self._defaults:
            try:
                validation_model = type(
                    f"{name}",
                    (BaseModel,),
                    {"__annotations__": attrs.get("__annotations__", {})},
                )
                validation_model(**self._defaults)
            except ValidationError as e:
                raise TypeError(f"Invalid default values in State class: {e}")

        for key in self._defaults:
            delattr(self, key)

    def __getattr__(self, name):
        return getattr(self.get_instance(), name)

    def get_instance(self):
        from ...core.app import Quillion

        app = Quillion._instance
        if app is None or app.websocket is None:
            raise RuntimeError("No active WebSocket connection for state access")
        if not hasattr(app, "_state_instances"):
            app._state_instances = {}
        if self not in app._state_instances:
            app._state_instances[self] = State(self)
        return app._state_instances[self]

    def set(self, **kwargs):
        instance = self.get_instance()
        for name, value in kwargs.items():
            if name in instance._data:
                if hasattr(self, "__annotations__") and name in self.__annotations__:
                    try:
                        validation_model = type(
                            f"ValidationModel",
                            (BaseModel,),
                            {"__annotations__": {name: self.__annotations__[name]}},
                        )
                        validation_model(**{name: value})
                    except ValidationError as e:
                        raise TypeError(
                            f"Invalid value for state variable '{name}': {e}"
                        )

                old_value = instance._data[name]
                instance._data[name] = value
                if old_value != value and instance._rerender_callback:
                    callback_result = instance._rerender_callback()
                    if inspect.iscoroutine(callback_result):
                        asyncio.create_task(callback_result)


class State(metaclass=StateMeta):
    _rerender_callback: Optional[Callable[[], Any]] = None

    def __init__(self, cls):
        self._cls = cls
        self._data = {k: v for k, v in cls._defaults.items()}

    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        return super().__getattribute__(name)

    def _set_rerender_callback(self, callback: Callable[[], Any]):
        self._rerender_callback = callback
