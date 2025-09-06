import re
from enum import Enum, auto
from typing import Dict, Tuple, Optional, Union, Pattern


class RouteType(Enum):
    REGEX_PATTERN = auto()  # re.Pattern
    REGEX_STRING = auto()  # regex:
    CATCH_ALL = auto()  # .* / *
    DYNAMIC = auto()  # {param} / *
    STATIC = auto()


class RegexParser:
    @staticmethod
    def compile_route(route: Union[str, Pattern]) -> Tuple[Pattern, RouteType]:
        if isinstance(route, Pattern):
            return route, RouteType.REGEX_PATTERN

        if isinstance(route, str) and route.startswith("regex:"):
            regex_pattern = route[6:].strip()
            return re.compile(regex_pattern), RouteType.REGEX_STRING

        if route in [".*", "*"]:
            return re.compile(r".*"), RouteType.CATCH_ALL

        if "{" in route or "*" in route:
            pattern = re.escape(route)
            pattern = re.sub(r"\\\{(\w+)\\\}", r"(?P<\1>[^\/]+)", pattern)
            pattern = pattern.replace(r"\*", r"[^\/]+")
            return re.compile(f"^{pattern}$"), RouteType.DYNAMIC

        pattern = re.escape(route)
        return re.compile(f"^{pattern}$"), RouteType.STATIC

    @staticmethod
    def get_route_type(route: Union[str, Pattern]) -> RouteType:
        if isinstance(route, Pattern):
            return RouteType.REGEX_PATTERN

        if isinstance(route, str) and route.startswith("regex:"):
            return RouteType.REGEX_STRING

        if route in [".*", "*"]:
            return RouteType.CATCH_ALL

        if "{" in route or "*" in route:
            return RouteType.DYNAMIC

        return RouteType.STATIC

    @staticmethod
    def extract_params(pattern: Pattern, path: str) -> Optional[Dict]:
        match = pattern.match(path)
        return match.groupdict() if match else None

    @staticmethod
    def get_clean_class_name(route: Union[str, Pattern]) -> str:
        if isinstance(route, Pattern):
            route_str = route.pattern
        else:
            route_str = str(route)

        clean_router = route_str.strip("/").replace("/", "-")

        clean_router = re.sub(r"[^a-zA-Z0-9_-]", "", clean_router)

        if not clean_router or clean_router == "regex":
            clean_router = "dynamic"

        return clean_router
