from typing import Callable


def style(func: Callable) -> Callable:
    func._is_style = True
    return func
