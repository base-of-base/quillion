"""Type compatibility and imports for TYPE_CHECKING."""

from __future__ import annotations

import math
import operator
import uuid
from weakref import WeakKeyDictionary

from .. import _context as ctx
from ..components.base import Component
from ..session import Session

__all__ = [
    "Component",
    "Session",
    "WeakKeyDictionary",
    "ctx",
    "math",
    "operator",
    "uuid",
]
