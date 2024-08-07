from io import BytesIO
from reportlab.pdfgen import canvas
from PIL import Image

from config.config import Config
from game.game import Game

config = Config()

def convert_image_to_pdf(filename, difficulty, grid_size, puzzle_title):
    width_in_pxls_max = get_width_in_pxls_max(grid_size)
    height_in_pxls_max = width_in_pxls_max
    max_length = get_max_length(difficulty)

    the_game = Game(filename, width_in_pxls_max, height_in_pxls_max, max_length)
    pdf_io = the_game.to_pdf(puzzle_title, show_solution=False, download=True)
    return pdf_io

def get_width_in_pxls_max(grid_size):
    if grid_size == 'small':
        return config['SMALL_GRID_WIDTH_HEIGHT']
    elif grid_size == 'medium':
        return config['MEDIUM_GRID_WIDTH_HEIGHT']
    elif grid_size == 'large':
        return config['LARGE_GRID_WIDTH_HEIGHT']

    raise ValueError('grid_size was not one of `small`, `medium` or `large`.')

def get_max_length(difficulty):
    diff_1_max_len = config['DIFFICULTY_1_MAX_LENGTH']
    diff_10_max_len = config['DIFFICULTY_10_MAX_LENGTH']
    n_from_1 = difficulty - 1
    n_from_10 = 10 - difficulty
    span = 10 - 1
    lower_weight = n_from_10 / span
    upper_weight = n_from_1 / span
    result = diff_1_max_len * lower_weight + diff_10_max_len * upper_weight
    result = int(result)
    return result