from image.point import Point
from image.colour import Colour

class Pixel:
    def __init__(self, point, colour):
        if not isinstance(point, Point):
            raise ValueError('Parameter `point` is not of type `Point`')
        
        if not isinstance(colour, Colour):
            raise ValueError('Parameter `colour` is not of type `Colour`')
        
        self.point = point
        self.colour = colour
        self.route = None

    def put_on_route(self, route):
        self.route = route

    def finalise(self):
        self.colour = Colour.finalised_colour()