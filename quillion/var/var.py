"""Var class - reactive variable that tracks changes."""

from __future__ import annotations

import ast
import importlib.abc
import importlib.machinery
import importlib.util
import sys
import types
import uuid
from typing import Any, Callable, Optional, List, TYPE_CHECKING
from weakref import WeakKeyDictionary

if TYPE_CHECKING:
    from ..components.base import Component
    from ..session import Session

from .. import _context as ctx
from .reactive_expression import ReactiveExpression
from .var_operator import VarOperator
from .formatted_var import FormattedVar
from .proxy import ReactiveProxy

__all__ = ["Var", "var", "auto_name_vars"]


class Var(ReactiveExpression):
    """Reactive variable that tracks changes and notifies observers."""
    _key: str
    _initial: Any
    _observers: WeakKeyDictionary
    _raw_callbacks: List[Callable]
    _component_factory: Optional[Callable[..., "Component"]]
    _auto_named: bool

    def __init__(self, initial_value: Any = "") -> None:
        """Initialize a reactive variable with an optional initial value."""
        self._key = str(uuid.uuid4())
        self._initial = self._wrap_value(initial_value)
        self._observers = WeakKeyDictionary()
        self._raw_callbacks = []
        self._component_factory = None
        self._auto_named = False

    def _set_stable_key(self, name: str) -> None:
        """Set a stable key for this variable based on a name."""
        if name in ctx.VAR_NAME_REGISTRY:
            self._key = ctx.VAR_NAME_REGISTRY[name]
        else:
            ctx.VAR_NAME_REGISTRY[name] = self._key
        self._auto_named = True

    def _wrap_value(self, value: Any) -> Any:
        """Wrap mutable values in ReactiveProxy to track mutations."""
        # Не оборачиваем примитивные типы
        if isinstance(value, (str, int, float, bool, type(None), bytes)):
            return value
        # Оборачиваем всё остальное (списки, словари, пользовательские классы)
        if isinstance(value, (list, dict, set)):
            return ReactiveProxy(value, self._notify_self)
        # Для пользовательских объектов
        if isinstance(value, object):
            return ReactiveProxy(value, self._notify_self)
        return value

    @property
    def value(self) -> Any:
        """Get the current value of the variable."""
        session = ctx.current_session.get()
        if session is None:
            return self._initial
        
        raw_value = session.state.get_var_value(self._key, self._initial)
        
        # Если значение не обёрнуто в прокси, оборачиваем
        if not isinstance(raw_value, ReactiveProxy):
            wrapped = self._wrap_value(raw_value)
            session.state.set_var_value(self._key, wrapped)
            return wrapped
        
        return raw_value

    @value.setter
    def value(self, new_value: Any) -> None:
        """Set the value of the variable and notify observers."""
        session = ctx.current_session.get()
        if session is None:
            self._initial = self._wrap_value(new_value)
            return
        
        wrapped = self._wrap_value(new_value)
        session.state.set_var_value(self._key, wrapped)
        self._notify_self()

    def set(self, new_value: Any) -> None:
        """Set the value of the variable."""
        self.value = new_value

    def update(self, func: Callable[[Any], Any]) -> None:
        """Update the value by applying a function to the current value."""
        self.value = func(self.value)

    def append(self, suffix: str) -> VarOperator:
        """Append a suffix to the string representation."""
        return VarOperator(self, lambda a, b: str(a) + b, suffix)  # type: ignore

    def _notify_self(self) -> None:
        """Notify all observers of a change."""
        session = ctx.current_session.get()
        if session is not None:
            self._notify(session)

    def __bool__(self) -> bool:
        """Boolean conversion."""
        return bool(self.value)

    def __len__(self) -> int:
        """Length of the value."""
        return len(self.value)

    def __contains__(self, item: Any) -> bool:
        """Check if item is in the value."""
        return item in self.value

    def __str__(self) -> str:
        """String representation of the value."""
        return str(self.value)

    def __format__(self, format_spec: str) -> str:
        """Return a FormattedVar that reacts to changes."""
        return FormattedVar(format(self.value, format_spec), self, format_spec)

    def __int__(self) -> int:
        """Integer conversion."""
        return int(self.value)

    def __float__(self) -> float:
        """Float conversion."""
        return float(self.value)

    def __repr__(self) -> str:
        """Detailed representation of the variable."""
        return f"Var({repr(self.value)})"

    def __call__(self, *args, as_component=None, **kwargs) -> Any:
        """Set value: counter(42). Create two-way component: counter().
        Returns self after setting, or a Component when creating a binding."""
        if args and len(args) == 1 and as_component is None and not kwargs:
            self.value = args[0]
            return self
        from ..components.two_way import TwoWayBindingElement
        if self._component_factory is not None:
            return self._component_factory(bind_var=self, *args, **kwargs)
        if as_component is not None:
            if isinstance(as_component, str):
                comp_cls = ctx.TWO_WAY_REGISTRY[as_component]
            elif issubclass(as_component, TwoWayBindingElement):
                comp_cls = as_component
            else:
                raise TypeError("as_component must be a string alias or TwoWayBindingElement subclass")
        else:
            if ctx.default_two_way_class is None:
                raise RuntimeError("No default two-way component registered.")
            comp_cls = ctx.default_two_way_class
        return comp_cls(bind_var=self, *args, **kwargs)

    def bind_with(self, component_factory: Callable[..., "Component"]) -> "Var":
        """Bind this variable to a component factory for two-way binding."""
        self._component_factory = component_factory
        return self

    def _notify(self, session: "Session") -> None:
        """Notify all observers of a change."""
        for observer, callbacks in list(self._observers.items()):
            for cb in callbacks:
                cb(observer, self, session)
        for cb in self._raw_callbacks:
            cb(self, session)

    def observe(self, comp: "Component", cb: Callable) -> None:
        """Register an observer component and callback."""
        if comp not in self._observers:
            self._observers[comp] = []
        self._observers[comp].append(cb)

    def _add_raw_callback(self, cb: Callable) -> Callable[[], None]:
        """Add a raw callback that receives (var, session) on changes."""
        self._raw_callbacks.append(cb)
        def unsubscribe():
            if cb in self._raw_callbacks:
                self._raw_callbacks.remove(cb)
        return unsubscribe


def var(initial_value: Any = "", *, name: Optional[str] = None) -> Var:
    """Create a reactive variable with an optional stable name."""
    v = Var(initial_value)
    if name is not None:
        v._set_stable_key(name)
    return v


def auto_name_vars(module: Any) -> None:
    """Automatically assign stable names to all Var instances in a module."""
    for var_name, obj in module.__dict__.items():
        if isinstance(obj, Var) and not obj._auto_named:
            obj._set_stable_key(var_name)


# ── AST import hook: transform `counter = 42` to `counter.set(42)` ──

class _ReactiveVarTransformer(ast.NodeTransformer):
    """Finds reactive var names from `counter = var(...)` definitions,
    then rewrites `counter = <expr>` assignments to `counter.set(<expr>`."""

    def __init__(self) -> None:
        self.reactive_names: set[str] = set()

    def visit_Assign(self, node: ast.Assign) -> Any:
        if (
            isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == 'var'
        ):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.reactive_names.add(target.id)
        return node

    def _replace_assign(self, node: ast.Assign) -> Any:
        """If this is a reactive var assignment, replace with .set() call."""
        for target in node.targets:
            if (
                isinstance(target, ast.Name)
                and target.id in self.reactive_names
                and not self._is_var_factory(node.value)
            ):
                return ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id=target.id, ctx=ast.Load()),
                            attr='set',
                            ctx=ast.Load(),
                        ),
                        args=[node.value],
                        keywords=[],
                    )
                )
        return node

    def _process_body(self, body: list) -> list:
        """Recursively process statements, replacing reactive var assignments."""
        for node in body:
            if isinstance(node, ast.Assign):
                # Replace in-place via parent handling in caller
                pass
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._process_body(node.body)
            elif isinstance(node, ast.For):
                self._process_body(node.body)
                if node.orelse:
                    self._process_body(node.orelse)
            elif isinstance(node, ast.While):
                self._process_body(node.body)
                if node.orelse:
                    self._process_body(node.orelse)
            elif isinstance(node, ast.If):
                self._process_body(node.body)
                if node.orelse:
                    self._process_body(node.orelse)
            elif isinstance(node, ast.With):
                self._process_body(node.body)
            elif isinstance(node, ast.ExceptHandler):
                self._process_body(node.body)
        # Second pass: replace assignments in this body level
        for i, node in enumerate(body):
            if isinstance(node, ast.Assign):
                replacement = self._replace_assign(node)
                body[i] = replacement
        return body

    def transform(self, tree: ast.Module) -> ast.Module:
        # First pass: find all reactive var names
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                self.visit_Assign(node)
        # Second pass: recursively replace assignments everywhere
        tree.body = self._process_body(tree.body)
        return tree

    @staticmethod
    def _is_var_factory(node: ast.AST) -> bool:
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == 'var'
        )


class _ReactiveVarLoader(importlib.abc.Loader):
    def __init__(self, source_path: str, original_loader: importlib.abc.Loader) -> None:
        self._source_path = source_path
        self._original_loader = original_loader

    def get_source(self, fullname: str) -> str:
        return self._original_loader.get_source(fullname)

    def get_code(self, fullname: str) -> types.CodeType:
        source = self.get_source(fullname)
        if source is None:
            return self._original_loader.get_code(fullname)
        try:
            tree = ast.parse(source, filename=self._source_path)
            transformer = _ReactiveVarTransformer()
            transformer.transform(tree)
            ast.fix_missing_locations(tree)
            return compile(tree, self._source_path, 'exec')
        except SyntaxError:
            pass
        return self._original_loader.get_code(fullname)

    def is_package(self, fullname: str) -> bool:
        return self._original_loader.is_package(fullname)

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        code = self.get_code(module.__name__)
        if code is None:
            raise ImportError(f"Cannot load module {module.__name__}")
        exec(code, module.__dict__)


# Save reference to original PathFinder to avoid recursion
_PathFinder_find_spec = importlib.machinery.PathFinder.find_spec.__func__


class _ReactiveVarFinder:
    _installed = False

    @classmethod
    def install(cls) -> None:
        if cls._installed:
            return
        cls._installed = True
        sys.meta_path.insert(0, cls())

    def find_spec(self, fullname: str, path=None, target=None):
        # Only intercept non-quillion modules (user code)
        if 'quillion' in fullname:
            return None
        try:
            spec = _PathFinder_find_spec(importlib.machinery.PathFinder, fullname, path, target)
        except (ImportError, ModuleNotFoundError, AttributeError, RecursionError):
            return None
        if spec is None or spec.loader is None or isinstance(spec.loader, _ReactiveVarLoader):
            return None
        # Skip modules without Python source (built-in, frozen, C extensions)
        loader_name = type(spec.loader).__name__
        if loader_name in ('BuiltinImporter', 'FrozenImporter', 'ExtensionFileLoader'):
            return None
        return importlib.util.spec_from_loader(
            fullname,
            _ReactiveVarLoader(spec.origin or fullname, spec.loader),
            is_package=_ReactiveVarLoader(spec.origin or fullname, spec.loader).is_package(fullname),
            origin=spec.origin,
        )


_ReactiveVarFinder.install()


class VarNamespace:
    """Callable namespace for reactive variables.

    Supports var.counter = var(0) to create reactive vars,
    var.counter = 42 to set a Var's value reactively,
    and var(0) to create a new Var.
    """

    def __init__(self) -> None:
        self._vars: dict[str, Var] = {}

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Delegate to the var() factory function."""
        return var(*args, **kwargs)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('_'):
            object.__setattr__(self, name, value)
            return
        try:
            reactive_vars = object.__getattribute__(self, '_vars')
        except AttributeError:
            object.__setattr__(self, name, value)
            return
        if isinstance(value, Var):
            reactive_vars[name] = value
            if not value._auto_named:
                value._set_stable_key(name)
        elif name in reactive_vars:
            reactive_vars[name].value = value
        else:
            object.__setattr__(self, name, value)

    def __getattr__(self, name: str) -> Any:
        try:
            reactive_vars = object.__getattribute__(self, '_vars')
        except AttributeError:
            raise AttributeError(f"'VarNamespace' has no attribute '{name}'")
        if name in reactive_vars:
            return reactive_vars[name]
        raise AttributeError(f"'VarNamespace' has no attribute '{name}'")