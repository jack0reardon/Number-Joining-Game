from image.GreyscaleImage import GreyscaleImage
from Colour import Colour
from Point import Point, get_points_NSEW
from NumberPath import NumberPath
from copy import deepcopy
import numpy as np

class PathConstructor:
    __difficulty = 1

    def __init__(self, pixels):
        self.pixels = pixels

    def recalibrate(self):
        self.mandatory_hooks = []
        self.pixels[self.pixels != Colour.White] = Colour.Grey
        self.determine_mandatory_hooks()
    
    # def determine_mandatory_hooks(self):
    #     # These are just all external corners, initially
    #     width, height = self.greyscale_grid.shape
    #     for x in range(width):
    #         for y in range(height):
    #             curr_pnt = Point(x, y)
    #             if self.is_external_corner(curr_pnt):
    #                 self.mandatory_hooks.append(curr_pnt)

    # def get_next_mandatory_hook(self):
    #     return self.mandatory_hooks.pop() if self.mandatory_hooks else None

    # def propose_new_hook(self):
    #     width, height = self.greyscale_grid.shape
    #     for x in range(width):
    #         for y in range(height):
    #             if self.greyscale_grid[x, y] != Colour.White:
    #                 return Point(x, y)
        
    #     return None

    def get_next_hook(self):
        indices = np.argwhere(self.pixels == Colour.Grey)
        return tuple(indices[np.random.choice(len(indices))]) if indices.size else None

    def propose_new_path(self):
        curr_hook = self.get_next_hook()
        if curr_hook is not None:
            self.expand(curr_hook)
            curr_hook = self.get_next_hook()

    def expand(self, curr_hook):
        # Red for expansion
        self.pixels[curr_hook] = Colour.Red
        for get_point_dir in get_points_NSEW:
            coords.extend([get_point_dir(greyscale_image, curr_pnt)] if greyscale_image[get_point_dir(greyscale_image, curr_pnt)] == Colour.Grey else [])


    @classmethod
    def set_difficulty(cls, new_difficulty):
        cls.__difficulty = new_difficulty
    
    @classmethod
    def from_greyscale_image(cls, greyscale_image):
        number_joiners = []

        greyscale_image_tmp = deepcopy(greyscale_image)
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
            greyscale_image[curr_pnt] = Colour.Red
            explored_image[curr_pnt] = Colour.Red
            for get_point_dir in get_points_NSEW:
                coords.extend([get_point_dir(greyscale_image, curr_pnt)] if greyscale_image[get_point_dir(greyscale_image, curr_pnt)] == Colour.Grey else [])

        return explored_image
    
    def get_n_surrounding(self, curr_pnt):
        return sum([1 if self.pixels[get_point_dir(self.pixels, curr_pnt)] != Colour.White else 0 for get_point_dir in get_points_NSEW])
    
    def is_strip(self, curr_pnt):
        # NS or EW
        NS_count = sum([1 if self.pixels[get_point_dir(self.pixels, curr_pnt)] != Colour.White else 0 for get_point_dir in get_points_NS])
        EW_count = sum([1 if self.pixels[get_point_dir(self.pixels, curr_pnt)] != Colour.White else 0 for get_point_dir in get_points_EW])
        return NS_count == 2 ^ EW_count == 2
    
    # def is_corner(self, curr_pnt, external_or_internal='external'):
    #     valid_values = {'external': 2, 'internal': 3}
    #     if external_or_internal not in valid_values:
    #         raise ValueError(f'Should be one of {valid_values}')
        
    #     return not self.is_strip(curr_pnt) and self.get_n_surrounding(curr_pnt) == valid_values[external_or_internal]
    
    # def is_external_corner(self, curr_pnt):
    #     return self.is_corner(curr_pnt, 'external')
    
    # def is_internal_corner(self, curr_pnt):
    #     return self.is_corner(curr_pnt, 'internal')
    
    def __getitem__(self, point):
        if isinstance(point, Point):
            return self.pixels[point.x, point.y]
        elif isinstance(point, tuple):
            return self.pixels[point[0], point[1]]

        return None
    
    def __str__(self):
        return '\n'.join([''.join([str(x) if x != Colour.White else ' ' for x in row]) for row in self.pixels])
    

    


aaa = GreyscaleImage.from_filename('C:/Users/sexy0/Documents/Python/mona-lisa.jpg', x_dim_max = 30, y_dim_max = 30)
print(aaa)
bbb = PathConstructor.from_greyscale_image(aaa)
PathConstructor.set_difficulty(10)
for bb in bbb:
    print(bb)
