from dataclasses import dataclass
from typing import Any

from .pixel import Pixel

# Attribute 'other_route' will be None unless explicitly changed to reference another route
# This will only occur (by design) when the route extensions is joined onto another route
# See route.Route.join_to_route()
#
# Also, to avoid circular import, this module does not import Route and instead uses Any data type for other_route
@dataclass
class RouteExtension:
    next_pxl: Pixel
    is_from_end: bool
    other_route: Any = None
