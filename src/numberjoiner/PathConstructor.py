from ..image import GreyscaleImage
from .Colour import Colour
from .Point import Point
from copy import copy

class PathConstructor:
    def __init__(self, pixels):
        self.pixels = pixels
    
    @classmethod
    def from_greyscale_image(cls, greyscale_image):
        number_joiners = []

        greyscale_image_tmp = copy(greyscale_image)
        x_next, y_next = greyscale_image_tmp.get_a_grey_pixel()
        while x_next is not None:
            explored_image = PathConstructor.explore_from_x_y(greyscale_image_tmp, x_next, y_next)
            new_path_constructor = PathConstructor(explored_image.greyscale_grid)
            number_joiners.append(new_path_constructor)
            greyscale_image_tmp -= explored_image
            x_next, y_next = greyscale_image_tmp.get_a_grey_pixel()

        return number_joiners
    
    @staticmethod
    def explore_from_x_y(greyscale_image, x_start, y_start):
        explored_image = GreyscaleImage.blank_from_another_greyscale_image(greyscale_image)
        coords = [Point(x_start, y_start)]
        while len(coords) > 0:
            curr_pnt = coords.pop()
            # Mark as red = explored
            greyscale_image[curr_pnt.x, curr_pnt.y] = Colour.Red
            explored_image[curr_pnt.x, curr_pnt.y] = Colour.Grey
            coords.extend([Point(x - 1, y)] if greyscale_image[x - 1, y] == Colour.Grey else [])
            coords.extend([Point(x - 1, y)] if greyscale_image[x + 1, y] == Colour.Grey else [])
            coords.extend([Point(x, y - 1)] if greyscale_image[x, y - 1] == Colour.Grey else [])
            coords.extend([Point(x, y + 1)] if greyscale_image[x, y + 1] == Colour.Grey else [])
        
        return explored_image
    
aaa = GreyscaleImage.from_filename('C:/Users/sexy0/Documents/Python/mona-lisa.jpg', x_dim_max = 30, y_dim_max = 30)
print(aaa)
bbb = PathConstructor.from_greyscale_image(aaa)
for bb in bbb:
    print(bb)