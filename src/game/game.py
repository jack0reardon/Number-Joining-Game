from canvas.canvas import Canvas
from config.config import Config
from image.rgb_image import RGBImage
from image.colour import Colour

class Game:
    tester = 1

    def __init__(self, filename, width_in_pxls_max, height_in_pxls_max):
        config = Config()
        config.set_difficulty(10)

        rgb_image = RGBImage.from_filename(filename)
        rgb_image.fit_to_size(width_in_pxls_max, height_in_pxls_max)
        rgb_image.to_greyscale()
        
        canvas = Canvas.from_greyscale_image(rgb_image)
        canvas.grow_routes()
        self.game_pixels = canvas.get_canvas_as_game()

    def __str__(self):
        return '\n'.join([''.join([str(x) if x != Colour.WHITE else ' ' for x in row]) for row in self.game_pixels])


if __name__ == '__main__':
    the_game = Game('C:/Users/sexy0/Documents/Python/mona-lisa.jpg', width_in_pxls_max = 20, height_in_pxls_max = 20)
    print(the_game)