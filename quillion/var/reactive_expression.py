"""Reactive expression mixin with operator overloading."""

from __future__ import annotations

import math
import operator
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .computed_value import ComputedValue
    from .var_operator import VarOperator

from ._safe_op import _safe_op

__all__ = ["ReactiveExpression"]


class ReactiveExpression:
    """Mixin that provides reactive expression capabilities with operator overloading."""
    __slots__ = ()

    def _get_dependencies(self) -> list[ReactiveExpression]:
        """Return the dependencies of this expression."""
        if hasattr(self, '_dependencies'):
            return self._dependencies  # type: ignore
        return [self]

    def map(self, func: Callable[[Any], Any]) -> ComputedValue:
        """Transform the value using a function, returning a computed value."""
        from .computed_value import ComputedValue
        deps = self._get_dependencies()
        return ComputedValue(lambda: func(self.value), deps)

    def __neg__(self) -> ComputedValue:
        """Negation operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.neg, 0, self)

    def __pos__(self) -> ComputedValue:
        """Positive operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.pos, 0, self)

    def __abs__(self) -> ComputedValue:
        """Absolute value operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.abs, 0, self)

    def __invert__(self) -> ComputedValue:
        """Bitwise NOT operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.invert, 0, self)

    def __complex__(self) -> complex:
        """Convert to complex number."""
        return complex(self.value)

    def __index__(self) -> int:
        """Convert to index for slicing."""
        return operator.index(self.value)

    def __round__(self, ndigits: int | None = None) -> ComputedValue:
        """Round the value to specified digits."""
        from .computed_value import ComputedValue, _create_computed
        if ndigits is None:
            return _create_computed(round, self, 0)
        else:
            def calc() -> Any:
                return round(self.value, ndigits)
            deps = self._get_dependencies()
            return ComputedValue(calc, deps)

    def __floor__(self) -> ComputedValue:
        """Floor operator."""
        from .computed_value import _create_computed
        return _create_computed(math.floor, self, 0)

    def __ceil__(self) -> ComputedValue:
        """Ceil operator."""
        from .computed_value import _create_computed
        return _create_computed(math.ceil, self, 0)

    def __trunc__(self) -> ComputedValue:
        """Truncate operator."""
        from .computed_value import _create_computed
        return _create_computed(math.trunc, self, 0)

    def __add__(self, other: Any) -> VarOperator:
        """Addition operator."""
        from .var_operator import VarOperator
        if callable(other):
            return VarOperator(self, lambda a: b(a) if (b := other) else None, other)
        return VarOperator(self, lambda a: _safe_op(operator.add, a, other), other)

    def __radd__(self, other: Any) -> ComputedValue:
        """Right addition operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.add, other, self)

    def __sub__(self, other: Any) -> VarOperator:
        """Subtraction operator."""
        from .var_operator import VarOperator
        if callable(other):
            return VarOperator(self, lambda a: b(a) if (b := other) else None, other)
        return VarOperator(self, lambda a: _safe_op(operator.sub, a, other), other)

    def __rsub__(self, other: Any) -> ComputedValue:
        """Right subtraction operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.sub, other, self)

    def __mul__(self, other: Any) -> VarOperator:
        """Multiplication operator."""
        from .var_operator import VarOperator
        if callable(other):
            return VarOperator(self, lambda a: b(a) if (b := other) else None, other)
        return VarOperator(self, lambda a: _safe_op(operator.mul, a, other), other)

    def __rmul__(self, other: Any) -> ComputedValue:
        """Right multiplication operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.mul, other, self)

    def __truediv__(self, other: Any) -> VarOperator:
        """True division operator."""
        from .var_operator import VarOperator
        if callable(other):
            return VarOperator(self, lambda a: b(a) if (b := other) else None, other)
        return VarOperator(self, lambda a: _safe_op(operator.truediv, a, other), other)

    def __rtruediv__(self, other: Any) -> ComputedValue:
        """Right true division operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.truediv, other, self)

    def __floordiv__(self, other: Any) -> VarOperator:
        """Floor division operator."""
        from .var_operator import VarOperator
        if callable(other):
            return VarOperator(self, lambda a: b(a) if (b := other) else None, other)
        return VarOperator(self, lambda a: _safe_op(operator.floordiv, a, other), other)

    def __rfloordiv__(self, other: Any) -> ComputedValue:
        """Right floor division operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.floordiv, other, self)

    def __mod__(self, other: Any) -> VarOperator:
        """Modulo operator."""
        from .var_operator import VarOperator
        if callable(other):
            return VarOperator(self, lambda a: b(a) if (b := other) else None, other)
        return VarOperator(self, lambda a: _safe_op(operator.mod, a, other), other)

    def __rmod__(self, other: Any) -> ComputedValue:
        """Right modulo operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.mod, other, self)

    def __pow__(self, other: Any) -> VarOperator:
        """Power operator."""
        from .var_operator import VarOperator
        if callable(other):
            return VarOperator(self, lambda a: b(a) if (b := other) else None, other)
        return VarOperator(self, lambda a: _safe_op(operator.pow, a, other), other)

    def __rpow__(self, other: Any) -> ComputedValue:
        """Right power operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.pow, other, self)

    def __lshift__(self, other: Any) -> VarOperator:
        """Left shift operator (used for assignment binding)."""
        from .var_operator import VarOperator
        return VarOperator(self, lambda a, b: b, other)

    def __rshift__(self, other: Any) -> VarOperator:
        """Right shift operator."""
        from .var_operator import VarOperator
        if callable(other):
            return VarOperator(self, lambda a, b: other(a), other)
        return VarOperator(self, lambda a, b: b, other)

    def __eq__(self, other: object) -> ComputedValue:
        """Equality operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.eq, self, other)

    def __ne__(self, other: object) -> ComputedValue:
        """Inequality operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.ne, self, other)

    def __lt__(self, other: Any) -> ComputedValue:
        """Less than operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.lt, self, other)

    def __le__(self, other: Any) -> ComputedValue:
        """Less than or equal operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.le, self, other)

    def __gt__(self, other: Any) -> ComputedValue:
        """Greater than operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.gt, self, other)

    def __ge__(self, other: Any) -> ComputedValue:
        """Greater than or equal operator."""
        from .computed_value import _create_computed
        return _create_computed(operator.ge, self, other)
