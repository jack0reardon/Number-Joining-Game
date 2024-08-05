from dataclasses import dataclass

from .pixel import Pixel

@dataclass
class RouteExtension:
    next_pxl: Pixel
    is_from_end: bool

    @property
    def other_route(self):
        return self.next_pxl.route