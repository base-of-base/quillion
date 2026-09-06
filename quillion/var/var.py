"""Var class - reactive variable that tracks changes."""

from __future__ import annotations

import ast
import importlib.abc
import importlib.machinery
import importlib.util
import sys
import types
import uuid
import os
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
    _factory: Any
    _observers: WeakKeyDictionary
    _raw_callbacks: List[Callable]
    _component_factory: Optional[Callable[..., "Component"]]
    _auto_named: bool

    def __init__(self, initial_value: Any = "") -> None:
        """Initialize a reactive variable with an optional initial value."""
        self._key = str(uuid.uuid4())
        self._initial = initial_value
        self._observers = WeakKeyDictionary()
        self._raw_callbacks = []
        self._component_factory = None
        self._auto_named = False

        if isinstance(initial_value, (list, dict, set)):
            self._factory = lambda: type(initial_value)()
        elif hasattr(initial_value, "__class__") and hasattr(initial_value, "__init__"):
            try:
                self._factory = lambda: initial_value.__class__()
            except:
                self._factory = lambda: initial_value
        else:
            self._factory = lambda: initial_value

    def _set_stable_key(self, name: str) -> None:
        """Set a stable key for this variable based on a name."""
        if name in ctx.VAR_NAME_REGISTRY:
            self._key = ctx.VAR_NAME_REGISTRY[name]
        else:
            ctx.VAR_NAME_REGISTRY[name] = self._key
        self._auto_named = True

    def _wrap_value(self, value: Any) -> Any:
        """Wrap mutable values in ReactiveProxy to track mutations."""
        if isinstance(value, (str, int, float, bool, type(None), bytes)):
            return value
        if isinstance(value, (list, dict, set)):
            return ReactiveProxy(value, self._notify_self)
        if isinstance(value, object):
            return ReactiveProxy(value, self._notify_self)
        return value

    @property
    def value(self) -> Any:
        """Get the current value of the variable."""
        session = ctx.current_session.get()
        if session is None:
            return self._initial

        raw_value = session.state.get_var_value(self._key, None)

        if raw_value is None:
            new_value = self._factory()
            wrapped = self._wrap_value(new_value)
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

    def _notify_self(self) -> None:
        """Notify all observers of a change."""
        session = ctx.current_session.get()
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

    def __getattr__(self, name: str) -> Any:
        reserved = {
            '_key', '_initial', '_factory', '_observers', '_raw_callbacks',
            '_component_factory', '_auto_named', 'value', 'set', 'update',
            'observe', 'bind_with', 'map', '_notify_self',
            '_notify', '_add_raw_callback', '_set_stable_key', '_wrap_value'
        }
        if name.startswith('_') or name in reserved:
            raise AttributeError(name)

        value = self.value

        if not hasattr(value, name):
            raise AttributeError(f"'Var' object has no attribute '{name}'")

        attr = getattr(value, name)

        if not callable(attr):
            return attr

        def wrapper(*args, **kwargs):
            result = attr(*args, **kwargs)
            self._notify_self()
            return result

        return wrapper

    def __getitem__(self, key: Any) -> Any:
        return self.value[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        self.value[key] = value
        self._notify_self()

    def __delitem__(self, key: Any) -> None:
        del self.value[key]
        self._notify_self()

    def __iter__(self):
        return iter(self.value)

    def __len__(self):
        return len(self.value)

    def __contains__(self, item: Any) -> bool:
        return item in self.value


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


# ========== ТРАНСФОРМЕР ==========

class _ReactiveVarTransformer(ast.NodeTransformer):
    """
    Превращает все глобальные присваивания в реактивные переменные (var(...))
    и заменяет присваивания этим переменным внутри функций и лямбд на вызовы .set().
    """

    def __init__(self) -> None:
        # Имена реактивных переменных, определённых на верхнем уровне
        self.reactive_names: set[str] = set()
        # Флаг, нужно ли добавить импорт var
        self.needs_var_import: bool = False

    def _should_transform(self, filename: str) -> bool:
        """Проверяет, нужно ли трансформировать модуль."""
        if not filename:
            return False
        
        if 'site-packages' in filename:
            return False
        
        import sys
        for path in sys.path:
            if path and filename.startswith(path):
                if 'Lib' in path or 'lib' in path:
                    return False
                if 'venv' in path or '.venv' in path:
                    return False
                if 'python' in path.lower() and 'site-packages' not in path:
                    return False
                break
        
        import sysconfig
        stdlib_dir = sysconfig.get_path('stdlib')
        if stdlib_dir and filename.startswith(stdlib_dir):
            return False
        
        return True

    def _add_var_import(self, tree: ast.Module) -> ast.Module:
        """Добавляет импорт var в начало модуля, если его нет."""
        # Проверяем, есть ли уже импорт var
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom):
                    if node.module and 'quillion' in node.module:
                        for alias in node.names:
                            if alias.name == 'var':
                                return tree
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == 'quillion':
                            return tree
        
        # Добавляем импорт: from quillion import var
        import_node = ast.ImportFrom(
            module='quillion',
            names=[ast.alias(name='var', asname=None)],
            level=0,
        )
        tree.body.insert(0, import_node)
        return tree

    # ----- Глобальные присваивания (уровень модуля) -----
    def visit_Assign(self, node: ast.Assign) -> Any:
        if self._is_var_call(node.value):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.reactive_names.add(target.id)
            return node

        if self._is_special_assignment(node):
            return node

        self.needs_var_import = True
        new_value = self._wrap_in_var(node.value)
        new_node = ast.Assign(
            targets=node.targets,
            value=new_value,
            type_comment=node.type_comment,
        )
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.reactive_names.add(target.id)
        return new_node

    def visit_AnnAssign(self, node: ast.AnnAssign) -> Any:
        if not isinstance(node.target, ast.Name):
            return node

        if node.value and self._is_var_call(node.value):
            self.reactive_names.add(node.target.id)
            return node

        self.needs_var_import = True
        if node.value:
            new_value = self._wrap_in_var(node.value)
        else:
            new_value = ast.Call(
                func=ast.Name(id='var', ctx=ast.Load()),
                args=[],
                keywords=[],
            )
        new_node = ast.AnnAssign(
            target=node.target,
            annotation=node.annotation,
            value=new_value,
            simple=node.simple,
        )
        self.reactive_names.add(node.target.id)
        return new_node

    # ----- Обработка функций -----
    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        node.body = self._process_function_body(node.body)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
        node.body = self._process_function_body(node.body)
        return node

    # ----- Обработка вызовов (для лямбд в аргументах) -----
    def visit_Call(self, node: ast.Call) -> Any:
        """Обрабатываем вызовы функций - трансформируем лямбды в аргументах."""
        # Обрабатываем каждый позиционный аргумент
        new_args = []
        for arg in node.args:
            if isinstance(arg, ast.Lambda):
                # Трансформируем лямбду
                transformed = self.visit_Lambda(arg)
                new_args.append(transformed)
            elif isinstance(arg, ast.Call):
                # Рекурсивно обрабатываем вложенные вызовы
                new_args.append(self.visit_Call(arg))
            else:
                new_args.append(arg)
        
        # Обновляем позиционные аргументы
        node.args = new_args
        
        # Обрабатываем keyword аргументы
        new_keywords = []
        for kw in node.keywords:
            if isinstance(kw.value, ast.Lambda):
                transformed = self.visit_Lambda(kw.value)
                new_keywords.append(ast.keyword(arg=kw.arg, value=transformed))
            elif isinstance(kw.value, ast.Call):
                new_keywords.append(ast.keyword(arg=kw.arg, value=self.visit_Call(kw.value)))
            else:
                new_keywords.append(kw)
        node.keywords = new_keywords
        
        return node

    # ----- Обработка лямбд -----
    def visit_Lambda(self, node: ast.Lambda) -> Any:
        """Обрабатываем лямбды - заменяем body если нужно."""
        if isinstance(node.body, ast.BinOp):
            transformed = self._transform_binop(node.body)
            if transformed is not None:
                node.body = transformed
                self.needs_var_import = True
        elif isinstance(node.body, ast.Call):
            # Проверяем, не является ли это вызовом метода реактивной переменной
            transformed = self._transform_method_call(node.body)
            if transformed is not None:
                node.body = transformed
                self.needs_var_import = True
        elif isinstance(node.body, ast.UnaryOp):
            if isinstance(node.body.operand, ast.Name):
                name = node.body.operand.id
                if name in self.reactive_names:
                    self.needs_var_import = True
                    node.body = ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id=name, ctx=ast.Load()),
                            attr='set',
                            ctx=ast.Load(),
                        ),
                        args=[ast.UnaryOp(
                            op=node.body.op,
                            operand=ast.Attribute(
                                value=ast.Name(id=name, ctx=ast.Load()),
                                attr='value',
                                ctx=ast.Load(),
                            )
                        )],
                        keywords=[],
                    )
        elif isinstance(node.body, ast.Name):
            # Просто чтение переменной - ничего не делаем
            pass
        return node

    def _transform_binop(self, node: ast.BinOp) -> ast.AST | None:
        """Трансформирует бинарную операцию, если там есть реактивная переменная."""
        if isinstance(node.left, ast.Name):
            name = node.left.id
            if name in self.reactive_names:
                self.needs_var_import = True
                return ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id=name, ctx=ast.Load()),
                        attr='set',
                        ctx=ast.Load(),
                    ),
                    args=[ast.BinOp(
                        left=ast.Attribute(
                            value=ast.Name(id=name, ctx=ast.Load()),
                            attr='value',
                            ctx=ast.Load(),
                        ),
                        op=node.op,
                        right=node.right,
                    )],
                    keywords=[],
                )
        if isinstance(node.right, ast.Name):
            name = node.right.id
            if name in self.reactive_names:
                self.needs_var_import = True
                return ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id=name, ctx=ast.Load()),
                        attr='set',
                        ctx=ast.Load(),
                    ),
                    args=[ast.BinOp(
                        left=node.left,
                        op=node.op,
                        right=ast.Attribute(
                            value=ast.Name(id=name, ctx=ast.Load()),
                            attr='value',
                            ctx=ast.Load(),
                        ),
                    )],
                    keywords=[],
                )
        return None

    def _transform_method_call(self, node: ast.Call) -> ast.AST | None:
        """Трансформирует вызов метода реактивной переменной (например, items.append(...))."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                name = node.func.value.id
                if name in self.reactive_names:
                    # Оставляем как есть, но добавляем флаг
                    # Метод будет вызван через __getattr__ и вызовет _notify_self
                    self.needs_var_import = True
                    return node
        return None

    def _process_function_body(self, body: list) -> list:
        """Обрабатывает тело функции, заменяя присваивания глобальным реактивным переменным."""
        new_body = []
        for stmt in body:
            if isinstance(stmt, ast.Assign):
                new_stmt = self._transform_assign_in_function(stmt)
                if new_stmt is not None:
                    new_body.append(new_stmt)
                    self.needs_var_import = True
                else:
                    new_body.append(stmt)
            elif isinstance(stmt, ast.AugAssign):
                new_stmt = self._transform_aug_assign_in_function(stmt)
                if new_stmt is not None:
                    new_body.append(new_stmt)
                    self.needs_var_import = True
                else:
                    new_body.append(stmt)
            elif isinstance(stmt, ast.Expr):
                if isinstance(stmt.value, ast.Lambda):
                    new_lambda = self.visit_Lambda(stmt.value)
                    if new_lambda is not None:
                        new_body.append(ast.Expr(value=new_lambda))
                    else:
                        new_body.append(stmt)
                elif isinstance(stmt.value, ast.Call):
                    # Обрабатываем вызовы внутри функции
                    new_call = self.visit_Call(stmt.value)
                    new_body.append(ast.Expr(value=new_call))
                else:
                    new_body.append(stmt)
            elif isinstance(stmt, (ast.For, ast.While, ast.If, ast.With)):
                stmt.body = self._process_function_body(stmt.body)
                if hasattr(stmt, 'orelse') and stmt.orelse:
                    stmt.orelse = self._process_function_body(stmt.orelse)
                new_body.append(stmt)
            elif isinstance(stmt, ast.Return):
                if stmt.value is not None:
                    if isinstance(stmt.value, ast.BinOp):
                        transformed = self._transform_binop(stmt.value)
                        if transformed is not None:
                            stmt.value = transformed
                            self.needs_var_import = True
                    elif isinstance(stmt.value, ast.UnaryOp):
                        if isinstance(stmt.value.operand, ast.Name):
                            name = stmt.value.operand.id
                            if name in self.reactive_names:
                                self.needs_var_import = True
                                stmt.value = ast.Call(
                                    func=ast.Attribute(
                                        value=ast.Name(id=name, ctx=ast.Load()),
                                        attr='set',
                                        ctx=ast.Load(),
                                    ),
                                    args=[ast.UnaryOp(
                                        op=stmt.value.op,
                                        operand=ast.Attribute(
                                            value=ast.Name(id=name, ctx=ast.Load()),
                                            attr='value',
                                            ctx=ast.Load(),
                                        )
                                    )],
                                    keywords=[],
                                )
                    elif isinstance(stmt.value, ast.Call):
                        stmt.value = self.visit_Call(stmt.value)
                new_body.append(stmt)
            else:
                new_body.append(stmt)
        return new_body

    def _transform_assign_in_function(self, node: ast.Assign) -> ast.AST | None:
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in self.reactive_names:
                self.needs_var_import = True
                return ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id=name, ctx=ast.Load()),
                            attr='set',
                            ctx=ast.Load(),
                        ),
                        args=[node.value],
                        keywords=[],
                    )
                )
        return None

    def _transform_aug_assign_in_function(self, node: ast.AugAssign) -> ast.AST | None:
        if not isinstance(node.target, ast.Name):
            return None
        name = node.target.id
        if name not in self.reactive_names:
            return None

        self.needs_var_import = True
        left = ast.Attribute(
            value=ast.Name(id=name, ctx=ast.Load()),
            attr='value',
            ctx=ast.Load(),
        )
        bin_op = ast.BinOp(
            left=left,
            op=node.op,
            right=node.value,
        )
        return ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id=name, ctx=ast.Load()),
                    attr='set',
                    ctx=ast.Load(),
                ),
                args=[bin_op],
                keywords=[],
            )
        )

    def _is_var_call(self, node: ast.AST) -> bool:
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == 'var'
        )

    def _is_special_assignment(self, node: ast.Assign) -> bool:
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id.startswith('__'):
                return True
        if isinstance(node.value, (ast.Import, ast.ImportFrom)):
            return True
        if isinstance(node.value, (ast.FunctionDef, ast.ClassDef)):
            return True
        return False

    def _wrap_in_var(self, value_node: ast.AST) -> ast.Call:
        return ast.Call(
            func=ast.Name(id='var', ctx=ast.Load()),
            args=[value_node],
            keywords=[],
        )

    def _find_reactive_names(self, tree: ast.AST) -> None:
        """Находит все реактивные имена в AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if self._is_var_call(node.value):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            self.reactive_names.add(target.id)

    def transform(self, tree: ast.Module, filename: str = "") -> ast.Module:
        if not self._should_transform(filename):
            return tree

        # Сначала находим все реактивные имена
        self._find_reactive_names(tree)

        # Трансформируем тело модуля
        new_body = []
        for stmt in tree.body:
            if isinstance(stmt, ast.Assign):
                new_body.append(self.visit_Assign(stmt))
            elif isinstance(stmt, ast.AnnAssign):
                new_body.append(self.visit_AnnAssign(stmt))
            elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                new_body.append(self.visit(stmt))
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Lambda):
                new_lambda = self.visit_Lambda(stmt.value)
                new_body.append(ast.Expr(value=new_lambda))
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                # Обрабатываем вызовы на верхнем уровне (например, button(...))
                new_call = self.visit_Call(stmt.value)
                new_body.append(ast.Expr(value=new_call))
            elif isinstance(stmt, (ast.ClassDef, ast.For, ast.While, ast.If, ast.With)):
                new_body.append(self.generic_visit(stmt))
            else:
                new_body.append(stmt)

        tree.body = new_body
        
        # Добавляем импорт var если нужно
        if self.needs_var_import:
            tree = self._add_var_import(tree)
        
        return tree


# ========== ЗАГРУЗЧИК С ТРАНСФОРМЕРОМ ==========

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
            transformed_tree = transformer.transform(tree, filename=self._source_path)
            ast.fix_missing_locations(transformed_tree)
            return compile(transformed_tree, self._source_path, 'exec')
        except SyntaxError:
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


# ========== УСТАНОВКА FINDER ==========

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
        if 'quillion' in fullname:
            return None
        
        if fullname in sys.builtin_module_names:
            return None
        
        if hasattr(sys, 'stdlib_module_names'):
            if fullname in sys.stdlib_module_names:
                return None
            for stdlib_name in sys.stdlib_module_names:
                if fullname.startswith(stdlib_name + '.'):
                    return None
        
        try:
            spec = _PathFinder_find_spec(importlib.machinery.PathFinder, fullname, path, target)
        except (ImportError, ModuleNotFoundError, AttributeError, RecursionError):
            return None
        
        if spec is None or spec.loader is None or isinstance(spec.loader, _ReactiveVarLoader):
            return None
        
        loader_name = type(spec.loader).__name__
        if loader_name in ('BuiltinImporter', 'FrozenImporter', 'ExtensionFileLoader'):
            return None
        
        if spec.origin and 'site-packages' in spec.origin:
            return None
        
        if spec.origin:
            import sysconfig
            stdlib_dir = sysconfig.get_path('stdlib')
            if stdlib_dir and spec.origin.startswith(stdlib_dir):
                return None
        
        return importlib.util.spec_from_loader(
            fullname,
            _ReactiveVarLoader(spec.origin or fullname, spec.loader),
            is_package=_ReactiveVarLoader(spec.origin or fullname, spec.loader).is_package(fullname),
            origin=spec.origin,
        )


_ReactiveVarFinder.install()


class VarNamespace:
    """Callable namespace for reactive variables."""

    def __init__(self) -> None:
        self._vars: dict[str, Var] = {}

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
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