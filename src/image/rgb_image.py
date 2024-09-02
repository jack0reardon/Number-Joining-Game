from PIL import Image
import numpy as np
from warnings import warn

from .colour import Colour
from .point import Point
from config.config import Config

config = Config()

class RGBImage:
    def __init__(self, pixels):
        self.pixels = pixels
        self.pixels_fit_to_size = None
        self.pixels_fit_to_size_greyscale = None

    @classmethod
    def from_filename(cls, filename):
        image = Image.open(filename)
        image = image.convert('RGB')
        pixels = np.array(image)
        return cls(pixels)
    
    def fit_to_size(self, width_in_pxls_max, height_in_pxls_max):
        proposed_compression_factor = self.propose_compression_factor(width_in_pxls_max, height_in_pxls_max)
        self.fit_pixels_to_size(proposed_compression_factor)

    def fit_pixels_to_size(self, proposed_compression_factor):
        # Calculate the dimensions of the grid
        height, width, _ = self.pixels.shape
        grid_height, grid_height_remainder = divmod(height, proposed_compression_factor)
        grid_width, grid_width_remainder = divmod(width, proposed_compression_factor)

        # If the width or height are not evenly divided by proposed_compression_factor, then just crop it
        if grid_height_remainder != 0:
            grid_height -= 1
        
        if grid_width_remainder != 0:
            grid_width -= 1

        # Initialise an empty grid for averaged RGB values
        self.pixels_fit_to_size = np.zeros((grid_height, grid_width, 3), dtype=np.float32)

        # Iterate over each grid cell
        for i in range(grid_height):
            for j in range(grid_width):
                # Define the slice for the current grid cell
                y_start = i * proposed_compression_factor
                y_end = (i + 1) * proposed_compression_factor
                x_start = j * proposed_compression_factor
                x_end = (j + 1) * proposed_compression_factor

                # Extract the pixel group and calculate the average pixel value
                pixel_group = self.pixels[y_start:y_end, x_start:x_end]
                avg_rgb = np.mean(pixel_group, axis=(0, 1))
                self.pixels_fit_to_size[i, j] = avg_rgb

        # Convert the grid values to integers
        self.pixels_fit_to_size = self.pixels_fit_to_size.astype(np.uint8)

        return self.pixels_fit_to_size

    def to_greyscale(self, grey_percentile_cutoff=None):
        greyscale_from_rgb = RGBImage.apply_greyscale(self.pixels_fit_to_size)
        self.pixels_fit_to_size_greyscale = RGBImage.discretise_greyscale(greyscale_from_rgb, grey_percentile_cutoff)

    @staticmethod
    def apply_greyscale(rgb_grid):
        rgb_grid = rgb_grid.astype(np.float32)
        greyscale_from_rgb = 0.299 * (255 - rgb_grid[:, :, 0]) + 0.587 * (255 - rgb_grid[:, :, 1]) + 0.114 * (255 - rgb_grid[:, :, 2])
        return greyscale_from_rgb.astype(np.uint8)

    def propose_compression_factor(self, width_in_pxls_max, height_in_pxls_max):
        height_in_pxls_curr, width_in_pxls_curr, _ = self.pixels.shape
        proposed_compression_factor_max = width_in_pxls_curr // width_in_pxls_max
        square_height_max = height_in_pxls_curr // height_in_pxls_max
        proposed_compression_factor = max(proposed_compression_factor_max, square_height_max)
        return proposed_compression_factor

    def discretise_greyscale(greyscale_from_rgb, grey_percentile_cutoff):
        median_luminance = np.percentile(greyscale_from_rgb.flatten(), config.get('DEFAULT_GREY_PERCENTILE_CUTOFF', grey_percentile_cutoff))
        return np.where(greyscale_from_rgb < median_luminance, Colour.WHITE, Colour.GREY)
        
    def __str__(self):
        if self.pixels_fit_to_size_greyscale is None:
            return 'Printing an RGB image in the console as ASCII is currently limited to greyscale images. Need to convert to greyscale first. See `to_greyscale()`'
        
        return '\n'.join([''.join(['*' if x == Colour.Grey else ' ' for x in row]) for row in self.pixels_fit_to_size_greyscale])
