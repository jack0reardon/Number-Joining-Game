from enum import Enum

class Colour(Enum):
    WHITE = ' '
    GREY = '-'
    GREEN = '.'
    RED = '^'
    ORANGE = '*'

    @staticmethod
    def drawing_colour():
        return Colour.GREEN

    @staticmethod
    def route_start_stop_colour():
        return Colour.RED
    
    @staticmethod
    def confirmed_colour():
        return Colour.ORANGE