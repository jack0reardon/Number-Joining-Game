import numpy as np
from random import choice
from copy import copy

from image.colour import Colour
from image.point import Point
from .pixel import Pixel
from .route import Route
from .route_extension import RouteExtension
from config.config import Config

config = Config()

class Canvas:
    def __init__(self, pixels):
        self.pixels = pixels
        self.height, self.width = pixels.shape
        self.routes = None

    @classmethod
    def from_greyscale_image(cls, rgb_image):
        height, width = rgb_image.pixels_fit_to_size_greyscale.shape
        new_pixels = np.empty((height, width), dtype=object)
        routes = []
        for y in range(height):
            for x in range(width):
                point = Point(x, y)
                colour = rgb_image.pixels_fit_to_size_greyscale[y, x]
                
                if colour != Colour.WHITE:
                    colour = Colour.GREY
                
                new_pixel = Pixel(point, colour)
                new_pixels[y, x] = new_pixel

        result = cls(new_pixels)
        result.initialise_routes()
        return result
    
    def initialise_routes(self):
        self.routes = []
        for y in range(self.height):
            for x in range(self.width):
                if self.pixels[y, x].colour != Colour.WHITE:
                    new_route = Route.from_pxl(self.pixels[y, x])
                    self.routes.append(new_route)

    def get_initial_coloured_canvas(self):
        initial_coloured_canvas = np.empty((self.height, self.width), dtype=object)

        # First, paint it all white
        for y in range(self.height):
            for x in range(self.width):
                initial_coloured_canvas[y, x] = Colour.WHITE
        
        # Then paint in all the route starts and ends
        for route in self.routes:
            initial_coloured_canvas[route.path[0].point.y, route.path[0].point.x] = Colour.route_start_stop_colour()
            initial_coloured_canvas[route.path[-1].point.y, route.path[-1].point.x] = Colour.route_start_stop_colour()
        
        return initial_coloured_canvas

    def copy_coloured_canvas(self, coloured_canvas):
        initial_coloured_canvas = np.empty((self.height, self.width), dtype=object)

        # First, paint it all white
        for y in range(self.height):
            for x in range(self.width):
                initial_coloured_canvas[y, x] = coloured_canvas[y, x]

        return initial_coloured_canvas

    def get_routes_to_extend(self):
        return [r for r in self.routes if r.should_extend()]
    
    def get_next_route_to_extend(self):
        routes_to_extend = self.get_routes_to_extend()
        return choice(routes_to_extend) if routes_to_extend else None
    
    def get_next_pixel_for_new_route(self):
        new_route_pxls = self.get_new_route_pxls()

        if new_route_pxls.size == 0:
            return None
        
        next_pixel = np.random.choice(new_route_pxls)
        return next_pixel
    
    def extend_routes(self):
        route_to_extend = self.get_next_route_to_extend()
        n_unsuccessful_extension_attempts = 0
        while route_to_extend and n_unsuccessful_extension_attempts < config['MAX_N_UNSUCCESSFUL_EXTENSION_ATTEMPTS']:
            n_routes_before = len(self.routes)
            route_to_extend.extend(self)
            n_routes_after = len(self.routes)
            n_unsuccessful_extension_attempts += 1 if n_routes_before == n_routes_after else 0
            route_to_extend = self.get_next_route_to_extend()

    def remove_route(self, route_to_remove):
        assert route_to_remove is not None, 'Route does not exist'
        self.routes.remove(route_to_remove)

    def add_route(self, route_to_add):
        self.routes.append(route_to_add)
    
    def does_have_unique_solution(self, pxl_to_connect_A, pxl_to_connect_B):
        coloured_canvas = self.get_initial_coloured_canvas()
        n_solutions = self.get_n_solutions(coloured_canvas, pxl_to_connect_A, [pxl_to_connect_B])
        return n_solutions == 1

    def get_n_solutions(self, coloured_canvas, pxl_to_connect, other_pxls_to_connect):
        if pxl_to_connect is None:
            return 1
        
        n = pxl_to_connect.route.len
        solutions = self.seek_route_of_length_n(coloured_canvas, [pxl_to_connect], n)

        if not solutions:
            return 0
        
        n_solutions = 0
        for solution in solutions:
            last_pxl = solution[-1]
            other_route = last_pxl.route
            other_route_other_pixel = other_route.path[0] if last_pxl == other_route.path[-1] else other_route.path[-1]

            new_pxls_to_connect = {pxl for pxl in other_pxls_to_connect}
            curr_route_start_start_pxl = self.get_pixel_if_not_already_confirmed(solution[0].route.path[0], coloured_canvas)
            curr_route_start_end_pxl = self.get_pixel_if_not_already_confirmed(solution[0].route.path[-1], coloured_canvas)
            curr_route_end_start_pxl = self.get_pixel_if_not_already_confirmed(solution[-1].route.path[0], coloured_canvas)
            curr_route_end_end_pxl = self.get_pixel_if_not_already_confirmed(solution[-1].route.path[-1], coloured_canvas)
            new_pxls_to_connect.update(curr_route_start_start_pxl)
            new_pxls_to_connect.update(curr_route_start_end_pxl)
            new_pxls_to_connect.update(curr_route_end_start_pxl)
            new_pxls_to_connect.update(curr_route_end_end_pxl)
            new_pxls_to_connect.remove(solution[0])
            new_pxls_to_connect.remove(solution[-1])

            new_coloured_canvas = self.paint_canvas_with_solution(coloured_canvas, solution)

            next_pxl_to_connect = None

            if other_route_other_pixel == pxl_to_connect:
                # Just found the pre-existing route
                # Solidify this route and continue to connect other pixels
                if new_pxls_to_connect:
                    next_pxl_to_connect = new_pxls_to_connect.pop()
                else:
                    next_pxl_to_connect = None
            elif new_pxls_to_connect:
                # Prioritise the other route's other pixel
                next_pxl_to_connect = other_route_other_pixel
                new_pxls_to_connect.remove(next_pxl_to_connect)

            n_solutions += self.get_n_solutions(new_coloured_canvas, next_pxl_to_connect, new_pxls_to_connect)

            if n_solutions > 1:
                # There are already multiple solutions identified
                # Don't even bother looking through the other solutions
                return n_solutions
            
        return n_solutions
    
    def get_pixel_if_not_already_confirmed(self, pxl, coloured_canvas):
        return {pxl} if coloured_canvas[pxl.point.y, pxl.point.x] != Colour.confirmed_colour() else {}
    
    def paint_canvas_with_solution(self, coloured_canvas, solution):
        new_coloured_canvas = self.copy_coloured_canvas(coloured_canvas)
        for pxl in solution:
            new_coloured_canvas[pxl.point.y, pxl.point.x] = Colour.confirmed_colour()
        return new_coloured_canvas

    def seek_route_of_length_n(self, coloured_canvas, existing_path, n):
        curr_pxl = existing_path[-1]

        if len(existing_path) == n:
            if curr_pxl.colour == Colour.route_start_stop_colour() and curr_pxl.route.len == n:
                return [existing_path]
            else:
                return [[]]

        if len(existing_path) > 1 and curr_pxl.colour == Colour.route_start_stop_colour():
            # Reached another number too soon
            return [[]]
        
        adjacent_pxls_for_route_seek = self.get_adjacent_pxls_for_route_seek(coloured_canvas, curr_pxl, existing_path, n)
        all_routes = []
        for pxl in adjacent_pxls_for_route_seek:
            new_path = existing_path.copy()
            new_path.append(pxl)
            new_routes = self.seek_route_of_length_n(coloured_canvas, new_path, n)
            for new_route in new_routes:
                if len(new_route) > 0:
                    all_routes.append(new_route)
        
        return all_routes

    def get_adjacent_pxls_for_route_seek(self, coloured_canvas, curr_pxl, existing_path, n):
        adjacent_pxls_for_route_seek = []
        for pxl in self.get_pxls_NSEW(curr_pxl):
            pxl_colour = coloured_canvas[pxl.point.y, pxl.point.x]
            if pxl not in existing_path and \
                (pxl_colour == Colour.WHITE or \
                    (pxl_colour == Colour.route_start_stop_colour() and \
                     pxl.route.len == n)):
                adjacent_pxls_for_route_seek.append(pxl)
        
        return adjacent_pxls_for_route_seek
    
    def get_adjacent_pxls_for_extending_route(self, curr_pxl, route):
        adjacent_pxls = self.get_pxls_NSEW(curr_pxl)
        return [pxl for pxl in adjacent_pxls if pxl.colour == Colour.route_start_stop_colour() and pxl not in route.path]
    
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
        pnts = [func(point) for func in get_pnts_NSEW_funcs]
        return [pnt for pnt in pnts if pnt is not None]
    
    def get_pxls_NSEW(self, pixel):
        pnts_NSEW = self.get_pnts_NSEW(pixel.point)
        return [self[pnt] for pnt in pnts_NSEW if pnt is not None]
    
    def get_canvas_as_game_pixels(self):
        height, width = self.pixels.shape
        game_pixels = np.empty((height, width), dtype=object)
        game_pixels[:] = Colour.WHITE.value

        for route in self.routes:
            route_start = route.path[0]
            route_end = route.path[-1]
            route_len = str(route.len)
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
    

