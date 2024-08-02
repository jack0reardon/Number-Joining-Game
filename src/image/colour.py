from enum import Enum

class Colour(Enum):
    WHITE = ' '
    GREY = '-'
    GREEN = '.'
    YELLOW = '*'
    RED = '^'
    BLUE = '!'

    @property
    def drawing_colour(self):
        return Colour.GREEN
    
    @property
    def hook_colour(self):
        return Colour.YELLOW

    @property
    def route_start_stop_colour(self):
        return Colour.RED

    @property
    def finalised_colour(self):
        return Colour.BLUE

    def is_available_for_extending_route(self):
        return self in [Colour.GREY, Colour.route_start_stop_colour, Colour.hook_colour]