"""Type conversion strategies for operators."""

import operator
from typing import Any

__all__ = [
    "_OP_STRATEGIES",
    "_as_complex",
    "_as_float",
    "_as_is",
    "_as_str",
]


def _as_is(a: Any, b: Any) -> tuple[Any, Any]:
    """Return values as-is."""
    return a, b


def _as_float(a: Any, b: Any) -> tuple[float, float]:
    """Convert both values to float."""
    return float(a), float(b)


def _as_str(a: Any, b: Any) -> tuple[str, str]:
    """Convert both values to string."""
    return str(a), str(b)


def _as_complex(a: Any, b: Any) -> tuple[complex, complex]:
    """Convert both values to complex (for power operations)."""
    return complex(a), complex(b)


# Declarative strategies for operators
_OP_STRATEGIES = {
    # Arithmetic operations
    operator.add: (_as_is, _as_float, _as_str),
    operator.mul: (_as_is, _as_float, _as_str),
    operator.sub: (_as_is, _as_float),
    operator.truediv: (_as_is, _as_float),
    operator.floordiv: (_as_is, _as_float),
    operator.pow: (_as_is, _as_float, _as_complex),
    operator.mod: (_as_is, _as_float),
    
    # Comparison operations - try numeric first, then string
    operator.eq: (_as_is, _as_float, _as_str),
    operator.ne: (_as_is, _as_float, _as_str),
    operator.lt: (_as_is, _as_float, _as_str),
    operator.le: (_as_is, _as_float, _as_str),
    operator.gt: (_as_is, _as_float, _as_str),
    operator.ge: (_as_is, _as_float, _as_str),
}
