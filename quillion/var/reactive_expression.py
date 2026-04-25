"""Reactive expression mixin with operator overloading."""

from __future__ import annotations

import math
import operator
from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:
    from .computed_value import ComputedValue
    from .var_operator import VarOperator

from ._safe_op import _safe_op

__all__ = ["ReactiveExpression"]


class ReactiveExpression:
    """Mixin that provides reactive expression capabilities with operator overloading."""
    __slots__ = ()

    def map(self, func: Callable[[Any], Any]) -> "ComputedValue":
        """Transform the value using a function, returning a computed value."""
        from .computed_value import ComputedValue
        deps = self._dependencies if hasattr(self, '_dependencies') else [self]  # type: ignore
        return ComputedValue(lambda: func(self.value), deps)  # type: ignore

    # ----- unary operators -----
    def __neg__(self) -> "ComputedValue":
        """Negation operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.neg, 0, self)  # type: ignore

    def __pos__(self) -> "ComputedValue":
        """Positive operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.pos, 0, self)  # type: ignore

    def __abs__(self) -> "ComputedValue":
        """Absolute value operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.abs, 0, self)  # type: ignore

    def __invert__(self) -> "ComputedValue":
        """Bitwise NOT operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.invert, 0, self)  # type: ignore

    # ----- conversions -----
    def __complex__(self) -> complex:
        """Convert to complex number."""
        return complex(self.value)  # type: ignore

    def __index__(self) -> int:
        """Convert to index for slicing."""
        return operator.index(self.value)  # type: ignore

    # ----- rounding -----
    def __round__(self, ndigits: Optional[int] = None) -> "ComputedValue":
        """Round the value to specified digits."""
        from .computed_value import ComputedValue, _create_computed
        if ndigits is None:
            return _create_computed(round, self, 0)  # type: ignore
        else:
            def calc():
                return round(self.value, ndigits)  # type: ignore
            deps = self._dependencies if hasattr(self, '_dependencies') else [self]  # type: ignore
            return ComputedValue(calc, deps) # type: ignore

    def __floor__(self) -> "ComputedValue":
        """Floor operator."""
        from .computed_value import _create_computed
        return _create_computed(math.floor, self, 0)  # type: ignore

    def __ceil__(self) -> "ComputedValue":
        """Ceil operator."""
        from .computed_value import _create_computed
        return _create_computed(math.ceil, self, 0)  # type: ignore

    def __trunc__(self) -> "ComputedValue":
        """Truncate operator."""
        from .computed_value import _create_computed
        return _create_computed(math.trunc, self, 0)  # type: ignore

    # ----- binary operators -----
    def __add__(self, other: Any) -> "VarOperator":
        """Addition operator."""
        from .var_operator import VarOperator
        if callable(other):
            return VarOperator(self, lambda a, b: b(a), other)  # type: ignore
        return VarOperator(self, lambda a, b: _safe_op(operator.add, a, b), other)  # type: ignore

    def __radd__(self, other: Any) -> "ComputedValue":
        """Right addition operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.add, other, self)  # type: ignore

    def __sub__(self, other: Any) -> "VarOperator":
        """Subtraction operator."""
        from .var_operator import VarOperator
        if callable(other):
            return VarOperator(self, lambda a, b: b(a), other)  # type: ignore
        return VarOperator(self, lambda a, b: _safe_op(operator.sub, a, b), other)  # type: ignore

    def __rsub__(self, other: Any) -> "ComputedValue":
        """Right subtraction operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.sub, other, self)  # type: ignore

    def __mul__(self, other: Any) -> "VarOperator":
        """Multiplication operator."""
        from .var_operator import VarOperator
        if callable(other):
            return VarOperator(self, lambda a, b: b(a), other)  # type: ignore
        return VarOperator(self, lambda a, b: _safe_op(operator.mul, a, b), other)  # type: ignore

    def __rmul__(self, other: Any) -> "ComputedValue":
        """Right multiplication operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.mul, other, self)  # type: ignore

    def __truediv__(self, other: Any) -> "VarOperator":
        """True division operator."""
        from .var_operator import VarOperator
        if callable(other):
            return VarOperator(self, lambda a, b: b(a), other)  # type: ignore
        return VarOperator(self, lambda a, b: _safe_op(operator.truediv, a, b), other)  # type: ignore

    def __rtruediv__(self, other: Any) -> "ComputedValue":
        """Right true division operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.truediv, other, self)  # type: ignore

    def __floordiv__(self, other: Any) -> "VarOperator":
        """Floor division operator."""
        from .var_operator import VarOperator
        if callable(other):
            return VarOperator(self, lambda a, b: b(a), other)  # type: ignore
        return VarOperator(self, lambda a, b: _safe_op(operator.floordiv, a, b), other)  # type: ignore

    def __rfloordiv__(self, other: Any) -> "ComputedValue":
        """Right floor division operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.floordiv, other, self)  # type: ignore

    def __mod__(self, other: Any) -> "VarOperator":
        """Modulo operator."""
        from .var_operator import VarOperator
        if callable(other):
            return VarOperator(self, lambda a, b: b(a), other)  # type: ignore
        return VarOperator(self, lambda a, b: _safe_op(operator.mod, a, b), other)  # type: ignore

    def __rmod__(self, other: Any) -> "ComputedValue":
        """Right modulo operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.mod, other, self)  # type: ignore

    def __pow__(self, other: Any) -> "VarOperator":
        """Power operator."""
        from .var_operator import VarOperator
        if callable(other):
            return VarOperator(self, lambda a, b: b(a), other)  # type: ignore
        return VarOperator(self, lambda a, b: _safe_op(operator.pow, a, b), other)  # type: ignore

    def __rpow__(self, other: Any) -> "ComputedValue":
        """Right power operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.pow, other, self)  # type: ignore

    def __lshift__(self, other: Any) -> "VarOperator":
        """Left shift operator (used for assignment binding)."""
        from .var_operator import VarOperator
        return VarOperator(self, lambda a, b: b, other)  # type: ignore

    def __rshift__(self, other: Any) -> "VarOperator":
        """Right shift operator."""
        from .var_operator import VarOperator
        if callable(other):
            return VarOperator(self, lambda a, b: b(a), other)  # type: ignore
        return VarOperator(self, lambda a, b: b, other)  # type: ignore

    # ----- comparisons -----
    def __eq__(self, other: Any) -> "ComputedValue":
        """Equality operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.eq, self, other)  # type: ignore

    def __ne__(self, other: Any) -> "ComputedValue":
        """Inequality operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.ne, self, other)  # type: ignore

    def __lt__(self, other: Any) -> "ComputedValue":
        """Less than operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.lt, self, other)  # type: ignore

    def __le__(self, other: Any) -> "ComputedValue":
        """Less than or equal operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.le, self, other)  # type: ignore

    def __gt__(self, other: Any) -> "ComputedValue":
        """Greater than operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.gt, self, other)  # type: ignore

    def __ge__(self, other: Any) -> "ComputedValue":
        """Greater than or equal operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.ge, self, other)  # type: ignore
