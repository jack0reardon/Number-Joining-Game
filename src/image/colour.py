from enum import Enum

class Colour(Enum):
    WHITE = ' '
    GREY = '-'
    GREEN = '.'
    YELLOW = '*'
    RED = '^'
    BLUE = '!'

    @staticmethod
    def drawing_colour():
        return Colour.GREEN
    
    @staticmethod
    def hook_colour():
        return Colour.YELLOW

    @staticmethod
    def route_start_stop_colour():
        return Colour.RED

    @staticmethod
    def finalised_colour():
        return Colour.BLUE

    def is_available_for_extending_route(self):
        return self in [Colour.GREY, Colour.route_start_stop_colour(), Colour.hook_colour()]
    
    def is_available_for_new_route(self):
        return self in [Colour.GREY, Colour.hook_colour()]