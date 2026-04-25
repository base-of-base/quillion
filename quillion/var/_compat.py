"""Type compatibility and imports for TYPE_CHECKING."""

from __future__ import annotations

import uuid
import operator
import math
from typing import TYPE_CHECKING
from weakref import WeakKeyDictionary

if TYPE_CHECKING:
    from ..components.base import Component
    from ..session import Session

from .. import _context as ctx

__all__ = [
    "uuid",
    "operator",
    "math",
    "WeakKeyDictionary",
    "Component",
    "Session",
    "ctx",
]
