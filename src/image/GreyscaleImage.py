# import importlib.resources
# import io

from PIL import Image
import numpy as np
from ..numberjoiner.Colour import Colour

class GreyscaleImage:
    def __init__(self):
        self.greyscale_grid = None

    @classmethod
    def from_filename(cls, filename, x_dim_max, y_dim_max):
        result = cls()
        rgb_grid = GreyscaleImage.get_average_rgb_grid(filename, x_dim_max, y_dim_max)
        result.greyscale_grid = GreyscaleImage.get_greyscale(rgb_grid)
        return result

    @classmethod
    def blank_from_another_greyscale_image(cls, other):
        if not isinstance(other, GreyscaleImage):
            raise TypeError('Constructor only supported between GreyscaleImage instances')
        
        result = cls()
        result.greyscale_grid = np.array([[Colour.White for _ in range(other.greyscale_grid[0])] for _ in range(other.greyscale_grid)])
        return result
    
    @staticmethod
    def load_image(filename):
        # with importlib.resources.path(importlib.resources.files('image').joinpath('data'), filename) as file_path:
        #     with open(file_path, 'rb') as f:
        #         img = Image.open(io.BytesIO(f.read()))
        #     return img
        
        # with open(filename, 'rb') as f:
        #     img = Image.open(io.BytesIO(f.read()))
        # return img
        return None

    @staticmethod
    def compress_to_average_rgb_grid(image_array, square_width):
        # Calculate the dimensions of the grid
        height, width, _ = image_array.shape
        grid_height, grid_height_remainder = divmod(height, square_width)
        grid_width, grid_width_remainder = divmod(width, square_width)

        # If the width or height are not evenly divided by square_width, then just crop it
        if grid_height_remainder != 0:
            grid_height -= 1
        
        if grid_width_remainder != 0:
            grid_width -= 1

        # Initialize an empty grid for averaged RGB values
        average_rgb_grid = np.zeros((grid_height, grid_width, 3), dtype=np.float32)

        # Iterate over each grid cell
        for i in range(grid_height):
            for j in range(grid_width):
                # Define the slice for the current grid cell
                y_start = i * square_width
                y_end = (i + 1) * square_width
                x_start = j * square_width
                x_end = (j + 1) * square_width

                # Extract the pixel group and calculate the average pixel value
                pixel_group = image_array[y_start:y_end, x_start:x_end]
                avg_rgb = np.mean(pixel_group, axis=(0, 1))
                average_rgb_grid[i, j] = avg_rgb

        # Convert the grid values to integers
        average_rgb_grid = average_rgb_grid.astype(np.uint8)

        return average_rgb_grid

    @staticmethod
    def rgb_to_greyscale(rgb_grid):
        rgb_grid = rgb_grid.astype(np.float32)
        grey_grid = 0.299 * (255 - rgb_grid[:, :, 0]) + 0.587 * (255 - rgb_grid[:, :, 1]) + 0.114 * (255 - rgb_grid[:, :, 2])
        grey_grid = grey_grid.astype(np.uint8)
        return grey_grid

    @staticmethod
    def get_image_rgb(image_path):
        image = Image.open(image_path)
        image = image.convert('RGB')
        image_array = np.array(image)
        return image_array

    @staticmethod
    def get_pixel_grouping_square_width(image_array, x_dim_max, y_dim_max):
        height, width, _ = image_array.shape
        square_height_max = height // y_dim_max
        square_width_max = width // y_dim_max
        selected_divisor = max(square_height_max, square_width_max)
        return selected_divisor
        
    @staticmethod
    def get_average_rgb_grid(image_path, x_dim_max, y_dim_max):
        image_array = GreyscaleImage.get_image_rgb(image_path)
        square_width = GreyscaleImage.get_pixel_grouping_square_width(image_array, x_dim_max, y_dim_max)
        average_rgb_grid = GreyscaleImage.compress_to_average_rgb_grid(image_array, square_width)
        return average_rgb_grid

    @staticmethod
    def get_greyscale_pixels_calibrated(greyscale_pixels):
        median_luminance = np.percentile(greyscale_pixels.flatten(), 75)
        return np.where(greyscale_pixels < median_luminance, Colour.White, Colour.Grey)

    @staticmethod
    def get_greyscale(rgb_grid):
        greyscale_pixels = GreyscaleImage.rgb_to_greyscale(rgb_grid)
        greyscale_pixels_calibrated = GreyscaleImage.get_greyscale_pixels_calibrated(greyscale_pixels)
        return greyscale_pixels_calibrated
    
    def get_a_grey_pixel(self):
        width, height = self.greyscale_grid.shape
        for x in range(width):
            for y in range(height):
                if self.greyscale_grid[x, y] == Colour.Grey:
                    return x, y
        
        return None, None
    
    def __setitem__(self, x, y, value):
        self.greyscale_grid[x, y] = value
    
    def __sub__(self, other):
        if not isinstance(other, GreyscaleImage):
            raise TypeError('Subtraction only supported between Vector instances')

        if self.greyscale_grid.shape != other.greyscale_grid.shape:
            raise ValueError('Dimensions of two GreyscaleImages must be the same for subtraction')
        
        return np.array([[max(0, self.greyscale_grid[x, y] - other.greyscale_grid[x, y]) for x in range(self.greyscale_grid[0])] for y in range(self.greyscale_grid)])
        
    def __str__(self):
        return '\n'.join([''.join(['*' if x == Colour.Grey else ' ' for x in row]) for row in self.greyscale_grid])
