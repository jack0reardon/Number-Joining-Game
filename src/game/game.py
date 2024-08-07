from canvas.canvas import Canvas
from image.colour import Colour
from config.config import Config
from image.rgb_image import RGBImage
from canvas.pdf_file import PDFFile

config = Config()

class Game:
    def __init__(self, filename, width_in_pxls_max, height_in_pxls_max, max_length=None):
        config.set_max_length(max_length)

        rgb_image = RGBImage.from_filename(filename)
        rgb_image.fit_to_size(width_in_pxls_max, height_in_pxls_max)
        rgb_image.to_greyscale()
        
        canvas = Canvas.from_greyscale_image(rgb_image)
        canvas.extend_routes()
        self.game_pixels = canvas.get_canvas_as_game_pixels()

    def solve(self):
        assert self.game_pixels is not None


    def to_pdf(self, title  =None, show_solution=False, output_filename=None):
        assert self.game_pixels is not None
        pdf_file = PDFFile(title, show_solution, self.game_pixels)
        pdf_file.create(output_filename)

    def __str__(self):
        return '\n'.join([''.join([' ' + (' ' if int(x) < 10 else '') + str(x) if x != Colour.WHITE.value else '  .' for x in row]) for row in self.game_pixels])


if __name__ == '__main__':
    the_game = Game('C:/Users/sexy0/Documents/Python/mona-lisa.jpg', width_in_pxls_max = 20, height_in_pxls_max = 20, max_length = 20)
    the_game.to_pdf()
