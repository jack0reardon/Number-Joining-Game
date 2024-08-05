from warnings import warn
from random import random, choice

from .pixel import Pixel
from image.colour import Colour
from .route_extension import RouteExtension
from config.config import Config

config = Config()

class Route:
    def __init__(self):
        self.path = []

    @classmethod
    def from_pxl(cls, initial_pxl):
        result = cls()
        result.append(RouteExtension(initial_pxl, None))
        return result
    
    @classmethod
    def copy(cls, a_route):
        result = cls()
        result.path = a_route.path.copy()
        return result

    def append(self, route_extension):
        if route_extension.next_pxl in self.path:
            raise ValueError('Attempted to add `pxl` to path, but it''s already on it.', UserWarning)
        
        route_extension.next_pxl.colour = Colour.route_start_stop_colour()
        
        path_len = len(self.path)
        if path_len > 0:
            position_to_insert_pxl = path_len if route_extension.is_from_end else 0
            if path_len >= 2:
                self.path[position_to_insert_pxl].colour = Colour.drawing_colour()
            self.path.insert(position_to_insert_pxl, route_extension.next_pxl)
        else:
            self.path.append(route_extension.next_pxl)

        route_extension.next_pxl.put_on_route(self)

    def orientate_routes_for_join(self, route_extension):
        if not route_extension.is_from_end:
            # Connecting `self.path` to the other route from the path's start
            # Just reverse self's path
            self.path.reverse()

        other_route_is_from_end = route_extension.next_pxl.route.path[-1] == route_extension.next_pxl
        
        if other_route_is_from_end:
            # Same as above
            route_extension.next_pxl.route.path.reverse()

    def join_to_route(self, route_extension):
        self.orientate_routes_for_join(route_extension)
        self.path.extend(route_extension.next_pxl.route.path)
        for pxl in route_extension.next_pxl.route.path:
            pxl.route = self

    # def recolour_route(self):
    #     for pxl in self.path:
    #         colour_to_draw = Colour.route_start_stop_colour() if pxl in [self.path[0], self.path[-1]] else Colour.drawing_colour()
    #         pxl.colour = colour_to_draw
    #         pxl.route = self

    def reached_max_length(self):
        return self.len == config['DIFFICULTY']
    
    def should_extend(self):
        probability_of_extension = 0 if self.reached_max_length() else config['PROBABILITY_OF_EXTENDING_ROUTE']
        return random() < probability_of_extension

    def extend(self, canvas):               
        route_extension = self.get_next_route_extension(canvas)

        if route_extension.next_pxl is None:
            # Nowhere to extend to, so just return without extending
            return
        
        self.propose_extension(route_extension, canvas)

    def propose_extension(self, route_extension, canvas):
        # Retain a copy of the original in case things don't work out
        original_route_A_path = self.path.copy()
        original_route_B_path = route_extension.other_route.path.copy()

        self.join_to_route(route_extension)
        
        pxl_to_connect_A = self.path[0]
        pxl_to_connect_B = self.path[-1]

        has_unique_solution = canvas.does_have_unique_solution(pxl_to_connect_A, pxl_to_connect_B)

        if has_unique_solution:
            canvas.remove_route(route_extension.other_route)
            # self.recolour_route()
        else:
            # Reverse the preoposed extension!
            self.path = original_route_A_path
            route_extension.other_route.path = original_route_B_path
            for pxl in self.path:
                pxl.route = self
            for pxl in route_extension.other_route.path:
                pxl.route = route_extension.other_route


    def get_next_route_extension(self, canvas):
        next_pxl_from_end = self.get_next_pxl_random(self.path[-1], canvas)

        if next_pxl_from_end is not None:
            return RouteExtension(next_pxl_from_end, True)
        
        next_pxl_from_start = self.get_next_pxl_random(self.path[0], canvas)

        return RouteExtension(next_pxl_from_start, False)
    
    def get_next_pxl_random(self, curr_pxl, canvas):
        adjacent_pxls_for_extending_route = canvas.get_adjacent_pxls_for_extending_route(curr_pxl)

        if len(adjacent_pxls_for_extending_route) == 0:
            return None
        
        return choice(adjacent_pxls_for_extending_route)
    
    @property
    def len(self):
        return len(self.path)