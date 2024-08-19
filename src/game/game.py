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
        self.solution = canvas.routes
        self.game_pixels = canvas.get_canvas_as_game_pixels()

    def to_pdf(self, title=None, do_include_instructions=False, show_solution=False, output_filename=None, download=True):
        assert self.game_pixels is not None
        pdf_file = PDFFile(pdf_title=title, do_include_instructions=do_include_instructions, show_solution=show_solution, the_solution=self.solution, game_pixels=self.game_pixels)

        if download:
            return pdf_file.download()
        else:
            pdf_file.create(output_filename)
            return

    def __str__(self):
        return '\n'.join([''.join([' ' + (' ' if int(x) < 10 else '') + str(x) if x != Colour.WHITE.value else '  .' for x in row]) for row in self.game_pixels])


if __name__ == '__main__':
    the_game = Game('C:/Users/sexy0/Documents/Python/mona-lisa.jpg', width_in_pxls_max = 10, height_in_pxls_max = 10, max_length = 5)
    # the_game = Game('C:/Users/sexy0/Documents/Python/rectangle.png', width_in_pxls_max = 100, height_in_pxls_max = 100, max_length = 30)
    the_game.to_pdf(do_include_instructions=True, download=False, output_filename='with_instructions (solution).pdf', show_solution=True)
    the_game.to_pdf(do_include_instructions=False, download=False, output_filename='without_instructions (solution).pdf', show_solution=True)
    the_game.to_pdf(do_include_instructions=True, download=False, output_filename='with_instructions.pdf', show_solution=False)
    the_game.to_pdf(do_include_instructions=False, download=False, output_filename='without_instructions.pdf', show_solution=False)
    print(the_game)
