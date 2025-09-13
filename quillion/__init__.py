from typing import List
import nest_asyncio
from .core import *
from .pages import *
from . import components
from .utils import *

nest_asyncio.apply()

app = Quillion()

def css(files: List[str]):
    return app.css(files)
