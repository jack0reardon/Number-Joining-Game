from image import Colour, Point
from route import Route
from config import Config
from pixel import Pixel
from random import choice
import numpy as np

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
                colour = rgb_image.pixels_fit_to_size_greyscale[x, y]
                new_pixels[x, y] = Pixel(point, colour)

        return cls(new_pixels)

    def initialise_greyscale(self):
        non_white_pixels_indices = np.array([p.colour != Colour.WHITE for p in self.pixels])
        self.n_grey_pixels_remaining = non_white_pixels_indices.size
        self.pixels[non_white_pixels_indices] = Colour.GREY

    def colour_pxl_neighbours_as_hooks(self, pxl):
        hookable_pxls_NSEW = [pxl for pxl in self.get_pxls_NSEW(pxl) if pxl.colour == Colour.GREY]

        for pxl in hookable_pxls_NSEW:
            pxl.colour = Colour.hook_colour

    def get_next_pixel_for_extending_route(self):
        next_pxl_options = {route.path[0] for route in self.routes if not route.finalised}
        next_pxl_options.update({route.path[-1] for route in self.routes if not route.finalised})
        return choice(next_pxl_options)
    
    def get_grey_pixels_indices(self):
        return np.array([p.colour == Colour.GREY for p in self.pixels])
    
    def get_next_pixel_for_new_route(self):
        grey_pixels_indices = self.get_grey_pixels_indices()

        if grey_pixels_indices.size == 0:
            return None
        
        grey_pixels = self.pixels[grey_pixels_indices]
        next_pixel = np.random.choice(grey_pixels)
        return next_pixel
    
    @property
    def n_unfinalised_routes(self):
        assert self.routes, 'Must have at least one route!'
        return sum([1 if route.finalised else 0 for route in self.routes])
    
    def grow_routes(self):
        self.start_new_route()

        while self.n_unfinalised_routes > 0:
            self.grow_a_route()
    
    def grow_a_route(self):
        if self.n_grey_pixels_remaining > 0:
            self.start_new_route()
        else:
            self.extend_existing_routes()

    def extend_existing_routes(self):
        curr_pxl = self.get_next_pixel_for_extending_route()

        if curr_pxl is None:
            return
        
        curr_pxl.route.extend(self)
        
    
    def start_new_route(self):
        curr_pxl = self.get_next_pixel_for_new_route()

        if curr_pxl is None:
            return
        
        self.start_new_route_from(curr_pxl)

    def start_new_route_from(self, curr_pxl):
        new_route = Route()
        new_route.append(curr_pxl, from_end=True)
        self.routes.append(new_route)
        self.decrement_n_grey_pixels_remaining()
        curr_pxl.route.extend(self)

    def remove_routes(self, route_to_remove):
        if route_to_remove is not None:
            self.routes.remove(route_to_remove)

    def decrement_n_grey_pixels_remaining(self):
        self.n_grey_pixels_remaining -= 1

    def get_adjacent_pxls_for_extending_route(self, curr_pxl):
        return [pxl for pxl in self.get_pxls_NSEW(curr_pxl) if pxl.colour.is_available_for_extending_route()]
    
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
        for y in range(height):
            for x in range(width):
                route_length = len(self.pixels[x, y].route)
                value = route_length if self.pixels[x, y].colour == Colour.route_start_stop_colour else None
                game_pixels[x, y] = value

        return game_pixels
    
    def __getitem__(self, pnt_or_pxl_or_tuple):
        if isinstance(pnt_or_pxl_or_tuple, Point):
            return self.pixels[pnt_or_pxl_or_tuple.x, pnt_or_pxl_or_tuple.y]
        elif isinstance(pnt_or_pxl_or_tuple, Pixel):
            return self.pixels[pnt_or_pxl_or_tuple.point.x, pnt_or_pxl_or_tuple.point.y]
        elif isinstance(pnt_or_pxl_or_tuple, tuple):
            return self.pixels[pnt_or_pxl_or_tuple[0], pnt_or_pxl_or_tuple[1]]

        return None
    
    def __str__(self):
        return '\n'.join([''.join([str(x) if x != Colour.White else ' ' for x in row]) for row in self.pixels])
    

