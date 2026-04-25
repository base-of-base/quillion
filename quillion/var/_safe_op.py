"""Safe operator application with coercion strategies."""

from typing import Any, Callable, Iterable
import operator

from ._strategies import _OP_STRATEGIES, _as_is, _as_float, _as_str


__all__ = ["_safe_op", "_try_apply"]


def _try_apply(op: Callable, a: Any, b: Any, transforms: Iterable[Callable]) -> Any:
    """Try applying operation with a sequence of transformations."""
    for transform in transforms:
        try:
            x, y = transform(a, b)
            return op(x, y)
        except (TypeError, ValueError):
            continue
    raise TypeError(f"Operation {op.__name__} failed for values: {a!r}, {b!r}")


def _safe_op(op_func: Callable, a: Any, b: Any) -> Any:
    """
    Safely apply an operator with explicit coercion strategy.
    """
    if op_func is operator.mod:
        try:
            return _try_apply(op_func, a, b, _OP_STRATEGIES[operator.mod])
        except TypeError:
            return str(a) + str(b)
    
    strategies = _OP_STRATEGIES.get(op_func, (_as_is, _as_float, _as_str))
    
    try:
        return _try_apply(op_func, a, b, strategies)
    except TypeError:
        if op_func in (operator.eq, operator.ne, operator.lt, operator.le, operator.gt, operator.ge):
            return op_func(str(a), str(b))
        elif op_func in (operator.add, operator.mul):
            return op_func(str(a), str(b))
        else:
            raise TypeError(f"Cannot apply {op_func.__name__} to {type(a).__name__} and {type(b).__name__}")
