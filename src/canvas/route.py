from warnings import warn
from random import random, choice
from pixel import Pixel
from image import Colour
from route_extension import RouteExtension
from config import Config

config = Config()

class Route:
    def __init__(self):
        self.path = []
        self.finalised = False

    def append(self, route_extension):
        if not isinstance(route_extension.next_pxl, Pixel):
            raise ValueError('Attempted to append `pxl` to path, but not a Pixel or tuple object.', UserWarning)
        
        if route_extension.next_pxl in self.path:
            raise ValueError('Attempted to add `pxl` to path, but it''s already on it.', UserWarning)
        
        position_to_insert_pxl = -1 if route_extension.is_from_end else 0
        if len(self) >= 2:
            self.path[position_to_insert_pxl].colour = Colour.drawing_colour

        route_extension.next_pxl.colour = Colour.route_start_stop_colour

        self.path.insert(route_extension.next_pxl, position_to_insert_pxl)
        route_extension.next_pxl.put_on_route(self)

    def join_to_route(self, route_extension):
        route_extension.other_route = route_extension.next_pxls.route

        if not route_extension.is_from_end:
            # Connecting `self.path` to the other route from the path's start
            # Just reverse self's path
            self.path.reverse()

        other_is_from_end = route_extension.next_pxl.route.path[-1] == route_extension.next_pxl
        
        if other_is_from_end:
            # Same as above
            route_extension.next_pxl.route.reversed()

        self.path.extend(route_extension.next_pxl.route)

        for pxl in route_extension.next_pxl.route.path:
            colour_to_draw = Colour.route_start_stop_colour if pxl in [self.path[0], self.path[-1]] else Colour.drawing_colour
            pxl.colour = colour_to_draw
            pxl.route = self

    # Returns a route to release, if any, due to being joined via this extend() call
    def extend(self, canvas):
        if len(self) == config['DIFFICULTY']:
            # Reached the maximum length
            return None
        
        if not self.should_extend():
            return None
               
        route_extension = self.get_next_pxl(canvas)

        prior_pxl = self.path[-1 if route_extension.next_pxl_is_from_end else 0]

        if route_extension.next_pxl is None:
            # Nowhere to extend to, so just finalise this route
            self.finalise()
            return None
        
        # Even though the route has not actually been extended yet, just
        # assume it will be when the return statement is called afterwards
        canvas.decrement_n_grey_pixels_remaining()
        self.extend_from(route_extension)
    
        # If there is no `other_route`, the route was simply extended and not joined onto another route
        # Colour the neighbours of the prior pixel as the 'hook' colour to indicate
        # that there was an obstruction preventing an ambiguous route
        if route_extension.other_route is None:
            canvas.colour_pxl_neighbours_as_hooks(prior_pxl)

        canvas.remove_routes(route_extension.other_route)

    def extend_from(self, route_extension):
        if route_extension.next_pxl.colour == Colour.route_start_stop_colour:
            joining_route = route_extension.next_pxl.route
            self.join_to_route(route_extension)
        
        self.append(route_extension)
            
            
    def finalise(self):
        for pxl in self.path:
            pxl.finalise()
        
        self.finalised = True
            
    def should_extend(self):
        prob_extend_route = config['PROBABILITY_OF_EXTENDING_ROUTE']
        return random() < prob_extend_route
    
    def get_next_pxl(self, canvas):
        next_pxl_from_end = self.get_next_pxl_random(self.path[-1], canvas)

        if next_pxl_from_end is not None:
            return RouteExtension(next_pxl_from_end, True)
        
        return RouteExtension(self.get_next_pxl_random(self.path[0], canvas), False)
    
    def get_next_pxl_random(self, curr_pxl, canvas):
        adjacent_pxls_for_extending_route = canvas.get_adjacent_pxls_for_extending_route(curr_pxl)

        if len(adjacent_pxls_for_extending_route) == 0:
            return None
        
        return choice(adjacent_pxls_for_extending_route)
        
    def __len__(self):
        return len(self.path)