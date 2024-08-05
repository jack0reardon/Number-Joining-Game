import numpy as np
from random import choice

from image.colour import Colour
from image.point import Point
from .pixel import Pixel
from .route import Route
from .route_extension import RouteExtension

class Canvas:
    def __init__(self, pixels):
        self.pixels = pixels
        self.height, self.width = pixels.shape
        self.n_grey_pixels_remaining = None
        self.routes = []

        self.initialise_greyscale()

    @classmethod
    def from_greyscale_image(cls, rgb_image):
        height, width = rgb_image.pixels_fit_to_size_greyscale.shape
        new_pixels = np.empty((height, width), dtype=object)
        for y in range(height):
            for x in range(width):
                point = Point(x, y)
                colour = rgb_image.pixels_fit_to_size_greyscale[y, x]
                new_pixels[y, x] = Pixel(point, colour)

        return cls(new_pixels)

    def initialise_greyscale(self):
        height, width = self.pixels.shape
        self.n_grey_pixels_remaining = 0
        for y in range(height):
            for x in range(width):
                if self.pixels[y, x].colour != Colour.WHITE:
                    self.pixels[y, x].colour = Colour.GREY
                    self.n_grey_pixels_remaining += 1

    def colour_pxl_neighbours_as_hooks(self, pxl):
        hookable_pxls_NSEW = [hookable_pxl_NSEW for hookable_pxl_NSEW in self.get_pxls_NSEW(pxl) if hookable_pxl_NSEW.colour == Colour.GREY]

        for hookable_pxl_NSEW in hookable_pxls_NSEW:
            hookable_pxl_NSEW.colour = Colour.hook_colour()

    def get_next_route_to_extend(self):
        return choice([r for r in self.routes if not r.finalised])
    
    def get_new_route_pxls(self):
        return np.array([p for row in self.pixels for p in row if p.colour.is_available_for_new_route()])
    
    def get_next_pixel_for_new_route(self):
        new_route_pxls = self.get_new_route_pxls()

        if new_route_pxls.size == 0:
            return None
        
        next_pixel = np.random.choice(new_route_pxls)
        return next_pixel
    
    @property
    def n_unfinalised_routes(self):
        assert self.routes, 'Must have at least one route!'
        return sum([1 if not route.finalised else 0 for route in self.routes])
    
    def grow_routes(self):
        self.start_new_route()

        # By design, the second condition here (self.n_grey_pixels_remaining > 0)
        # is superfluous and is provided for clarity only. Considering the definition of grow_a_route()
        # further below, start_new_route() takes precedence over extend_existing_routes().
        # This will cause the canvas to initially be flooded with unfinalised routes. Hence,
        # n_grey_pixels_remaining > 0 implies n_unfinalised_routes > 0. The rare edge case
        # (when the one and only route is the entire and only grey area) terminates similarly
        # upon the call to extend_existing_routes ()
        while self.n_unfinalised_routes > 0 or self.n_grey_pixels_remaining > 0:
            self.grow_a_route()
    
    def grow_a_route(self):
        if self.n_grey_pixels_remaining > 0:
            self.start_new_route()
        else:
            self.extend_existing_routes()

    def extend_existing_routes(self):
        route_to_extend = self.get_next_route_to_extend()

        if route_to_extend is None:
            return
        
        route_to_extend.extend(self)
        
    
    def start_new_route(self):
        curr_pxl = self.get_next_pixel_for_new_route()

        if curr_pxl is None:
            return
        
        self.start_new_route_from(curr_pxl)

    def start_new_route_from(self, curr_pxl):
        new_route = Route()
        route_extension = RouteExtension(curr_pxl, None, None)
        new_route.append(route_extension)
        self.routes.append(new_route)
        self.decrement_n_grey_pixels_remaining()
        curr_pxl.route.extend(self)

    def remove_route(self, route_to_remove):
        if route_to_remove is not None:
            self.routes.remove(route_to_remove)

    def decrement_n_grey_pixels_remaining(self):
        self.n_grey_pixels_remaining -= 1

    def get_adjacent_pxls_for_extending_route(self, curr_pxl):
        adjacent_pxls = self.get_pxls_NSEW(curr_pxl)
        return [pxl for pxl in adjacent_pxls if pxl.colour.is_available_for_extending_route()]
    
    def get_pnt_within_canvas(self, x, y):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return None
        
        return Point(x, y)

    def get_pnt_N(self, point):
        return self.get_pnt_within_canvas(point.x, point.y - 1)
    
    def get_pnt_S(self, point):
        return self.get_pnt_within_canvas(point.x, point.y + 1)
    
    def get_pnt_E(self, point):
        return self.get_pnt_within_canvas(point.x + 1, point.y)
    
    def get_pnt_W(self, point):
        return self.get_pnt_within_canvas(point.x - 1, point.y)
    
    def get_pnts_NSEW(self, point):
        get_pnts_NSEW_funcs = [self.get_pnt_N, self.get_pnt_S, self.get_pnt_E, self.get_pnt_W]
        return [func(point) for func in get_pnts_NSEW_funcs]
    
    def get_pxls_NSEW(self, pixel):
        pnts_NSEW = self.get_pnts_NSEW(pixel.point)
        return [self[pnt] for pnt in pnts_NSEW if pnt is not None]
    
    def get_canvas_as_game(self):
        assert self.n_unfinalised_routes == 0
        height, width = self.pixels.shape
        game_pixels = np.empty((height, width), dtype=object)
        game_pixels[:] = Colour.WHITE.value

        for route in self.routes:
            route_start = route.path[0]
            route_end = route.path[-1]
            route_len = str(len(route))
            game_pixels[route_start.point.y, route_start.point.x] = route_len
            game_pixels[route_end.point.y, route_end.point.x] = route_len

        return game_pixels
    
    def __getitem__(self, pnt_or_pxl_or_tuple):
        if isinstance(pnt_or_pxl_or_tuple, Point):
            return self.pixels[pnt_or_pxl_or_tuple.y, pnt_or_pxl_or_tuple.x]
        elif isinstance(pnt_or_pxl_or_tuple, Pixel):
            return self.pixels[pnt_or_pxl_or_tuple.point.x, pnt_or_pxl_or_tuple.point.y]
        elif isinstance(pnt_or_pxl_or_tuple, tuple):
            return self.pixels[pnt_or_pxl_or_tuple[0], pnt_or_pxl_or_tuple[1]]

        return None
    
    def __str__(self):
        return '\n'.join([''.join([str(x) if x != Colour.White else ' ' for x in row]) for row in self.pixels])
    

