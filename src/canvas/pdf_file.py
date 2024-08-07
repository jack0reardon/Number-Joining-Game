from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

from config.config import Config

config = Config()

class PDFFile:
    def __init__(self, pdf_title, show_solution, game_pixels):
        self.title = pdf_title
        self.show_solution = show_solution
        self.game_pixels = game_pixels
        self.pdf_canvas = None

    def create(self, output_filename=None):
        self.pdf_canvas = canvas.Canvas('C:/Users/sexy0/Documents/' + PDFFile.get_output_filename(output_filename), pagesize=letter)
        self.include_content()
        self.pdf_canvas.save()

    def download(self):
        pdf_io = BytesIO()
        self.pdf_canvas = canvas.Canvas(pdf_io)
        self.include_content()
        self.pdf_canvas.save()
        # Move the buffer's position to the beginning
        pdf_io.seek(0)
        return pdf_io

    def include_content(self):
        self.include_title()
        self.include_grid()
        self.include_copyright()

    @staticmethod
    def get_output_filename(output_filename=None):
        return output_filename or 'jack.pdf'
    
    def include_title(self):
        pdf_page_width, pdf_page_height = letter
        self.include_centred_text(config.get('PDF_TITLE', self.title), config['PDF_TITLE_FONT_SIZE'], pdf_page_height - config['PDF_BORDER_WIDTH'] / 2)
    
    def include_grid(self):
        pdf_page_width, pdf_page_height = letter
        pdf_canvas_width = pdf_page_width - 2 * config['PDF_BORDER_WIDTH']
        pdf_canvas_height = pdf_page_height - 2 * config['PDF_BORDER_WIDTH']
        grid_height, grid_width = self.game_pixels.shape
        cell_width = pdf_canvas_width / grid_width
        cell_height = pdf_canvas_height / grid_height
        cell_width_height = min(cell_width, cell_height)
        x_border = (pdf_page_width - cell_width_height * grid_width) / 2
        y_border = (pdf_page_height - cell_width_height * grid_height) / 2

        font_size = cell_width_height * 0.6
        self.pdf_canvas.setFont(config['PDF_FONT_NAME'], font_size)

        for i in range(grid_height):
            for j in range(grid_width):
                x = x_border + j * cell_width_height
                y = pdf_page_height - y_border - (i + 1) * cell_width_height
                self.pdf_canvas.rect(x, y, cell_width_height, cell_width_height)
                text = str(self.game_pixels[i, j])
                text_width = self.pdf_canvas.stringWidth(text, config['PDF_FONT_NAME'], font_size)
                self.pdf_canvas.drawString(x + (cell_width_height - text_width) / 2, y + (cell_width_height - font_size) / 2, text)
    
    def include_copyright(self):
        self.include_centred_text(config['PDF_COPYRIGHT_TEXT'], config['PDF_COPYRIGHT_FONT_SIZE'], config['PDF_BORDER_WIDTH'] / 2)

    def include_centred_text(self, text, font_size, text_y):
        pdf_page_width, pdf_page_height = letter
        self.pdf_canvas.setFont(config['PDF_FONT_NAME'], font_size)
        text_width = self.pdf_canvas.stringWidth(text, config['PDF_FONT_NAME'], font_size)
        text_x = (pdf_page_width - text_width) / 2
        self.pdf_canvas.drawString(text_x, text_y, text)