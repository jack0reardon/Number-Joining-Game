from collections import namedtuple

# Attribute 'other_route' will be None unless explicitly changed to reference another route
# This will only occur (by design) when the route extensions is joined onto another route
# See route.Route.join_to_route()
RouteExtension = namedtuple('RouteExtension', 'next_pxl is_from_end other_route')