from typing import Dict, Tuple, Optional
import re
from .regex_parser import RegexParser
from ..pages.base import PageMeta


class RouteFinder:
    @staticmethod
    def _normalize_path(path: str) -> str:
        if not path or path == "/":
            return "/"

        path = path.strip("/")

        return f"/{path}"

    @staticmethod
    def find_route(path: str) -> Tuple[Optional[type], Optional[dict], float]:
        path = RouteFinder._normalize_path(path)
        path = path.strip()
        page_cls = None
        params = None
        max_priority = float("-inf")

        # check regex route
        for regex_pattern, (cls, priority) in PageMeta._regex_routes.items():
            match_params = RegexParser.extract_params(regex_pattern, path)
            if match_params is not None and priority > max_priority:
                page_cls, params, max_priority = cls, match_params, priority

        # check static routes
        if not page_cls:
            for route, (cls, priority) in PageMeta._registry.items():
                match_params = RegexParser.extract_params(cls._regex, path)
                if match_params is not None and priority > max_priority:
                    page_cls, params, max_priority = cls, match_params, priority

        # check dynamic routes
        if not page_cls:
            for route, (pattern, cls, priority) in PageMeta._dynamic_routes.items():
                match_params = RegexParser.extract_params(pattern, path)
                if match_params is not None and priority > max_priority:
                    page_cls, params, max_priority = cls, match_params, priority

        return page_cls, params, max_priority
