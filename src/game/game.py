from image import RGBImage, Colour
from canvas import Canvas
from config import Config

class Game:
    def __init__(self, filename, width_in_pxls_max, height_in_pxls_max):
        config = Config()

        rgb_image = RGBImage.from_filename(filename)
        rgb_image.fit_to_size(width_in_pxls_max, height_in_pxls_max)
        rgb_image.to_greyscale()
        
        canvas = Canvas.from_greyscale_image(rgb_image)
        canvas.grow_routes()
        self.game_pixels = canvas.get_canvas_as_game()

    def __str__(self):
        return '\n'.join([''.join([str(x) if x != Colour.White else ' ' for x in row]) for row in self.pixels])


if __name__ == '__main__':
    the_game = Game('C:/Users/sexy0/Documents/Python/mona-lisa.jpg', width_in_pxls_max = 20, height_in_pxls_max = 20)
    print(the_game)