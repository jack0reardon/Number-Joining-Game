from io import BytesIO
from zipfile import ZipFile

from config.config import Config
from game.game import Game

config = Config()

def create_zip_archive(pdfs_and_their_filenames):
    buffer = BytesIO()
    with ZipFile(buffer, 'w') as zipfile:
        for the_pdf, filename in pdfs_and_their_filenames:
            zipfile.writestr(filename, the_pdf.read())
    buffer.seek(0)
    return buffer

def convert_image_to_pdf(filename, difficulty, grid_size, grey_percentile_cutoff, puzzle_title, do_include_instructions):
    width_in_pxls_max = get_width_in_pxls_max(grid_size)
    height_in_pxls_max = width_in_pxls_max
    max_length = get_max_length(grid_size, difficulty)

    the_game = Game(filename, width_in_pxls_max, height_in_pxls_max, max_length)
    pdf_io = the_game.to_pdf(title=puzzle_title, do_include_instructions=do_include_instructions, show_solution=False, download=True)
    pdf_io_solution = the_game.to_pdf(title=puzzle_title, do_include_instructions=do_include_instructions, show_solution=True, download=True)
    return pdf_io, pdf_io_solution

def get_width_in_pxls_max(grid_size):
    if grid_size == 'small':
        return config['SMALL_GRID_WIDTH_HEIGHT']
    elif grid_size == 'medium':
        return config['MEDIUM_GRID_WIDTH_HEIGHT']
    elif grid_size == 'large':
        return config['LARGE_GRID_WIDTH_HEIGHT']

    raise ValueError('grid_size was not one of `small`, `medium` or `large`.')

def get_max_length(grid_size, difficulty):
    diff_1_max_len = config['DIFFICULTY_1_MAX_LENGTH']
    diff_10_max_len = config['DIFFICULTY_10_MAX_LENGTH']
    n_from_1 = difficulty - 1
    n_from_10 = 10 - difficulty
    span = 10 - 1
    lower_weight = n_from_10 / span
    upper_weight = n_from_1 / span
    proposed_max_length = diff_1_max_len * lower_weight + diff_10_max_len * upper_weight
    proposed_max_length = int(proposed_max_length)

    if grid_size == 'large':
        proposed_max_length = int(proposed_max_length * config['LARGE_GRID_DIFFICULTY_SCALAR_FACTOR'])

    return proposed_max_length