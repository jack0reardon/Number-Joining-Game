from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import pkg_resources

from config.config import Config

config = Config()

class PDFFile:
    def __init__(self, pdf_title, do_include_instructions, show_solution, the_solution, game_pixels):
        self.title = pdf_title
        self.do_include_instructions = do_include_instructions
        self.show_solution = show_solution
        self.the_solution = the_solution
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
        self.include_instructions()
        self.include_copyright()

    @staticmethod
    def get_output_filename(output_filename=None):
        return output_filename or 'jack.pdf'
    
    def include_title(self):
        pdf_page_width, pdf_page_height = letter
        self.include_centred_text(config.get('PDF_TITLE', self.title), config['PDF_TITLE_FONT_SIZE'], pdf_page_height - config['PDF_BORDER_WIDTH'] / 2)
    
    def include_grid(self):
        instructions_height = self.do_include_instructions * config['PDF_INSTRUCTIONS_HEIGHT']
        pdf_page_width, pdf_page_height = letter
        pdf_canvas_width = pdf_page_width - 2 * config['PDF_BORDER_WIDTH']
        pdf_canvas_height = pdf_page_height - 2 * config['PDF_BORDER_WIDTH'] - instructions_height
        grid_height, grid_width = self.game_pixels.shape
        cell_width = pdf_canvas_width / grid_width
        cell_height = pdf_canvas_height / grid_height
        cell_width_height = min(cell_width, cell_height)
        x_border = (pdf_page_width - cell_width_height * grid_width) / 2
        y_border = config['PDF_BORDER_WIDTH']

        font_size = cell_width_height * 0.6
        self.pdf_canvas.setFont(config['PDF_FONT_NAME'], font_size)

        if self.show_solution:
            # Red color for the solution line
            self.pdf_canvas.setStrokeColorRGB(1, 0, 0)
            for route in self.the_solution:
                if route.len == 1:
                    # Draw a cross
                    start_x = x_border + route.path[0].point.x * cell_width_height + cell_width_height / 4
                    start_y = pdf_page_height - y_border - route.path[0].point.y * cell_width_height - cell_width_height / 4
                    end_x = start_x + cell_width_height / 2
                    end_y = start_y - cell_width_height / 2
                    self.pdf_canvas.line(start_x, start_y, end_x, end_y)

                    start_x += cell_width_height / 2
                    end_x -= cell_width_height / 2
                    self.pdf_canvas.line(start_x, start_y, end_x, end_y)
                else:
                    zippered_path = [((pair[0].point.x, pair[0].point.y), (pair[1].point.x, pair[1].point.y)) for pair in zip(route.path, route.path[1:])]
                    for (start_col, start_row), (end_col, end_row) in zippered_path:
                        start_x = x_border + start_col * cell_width_height + cell_width_height / 2
                        start_y = pdf_page_height - y_border - start_row * cell_width_height - cell_width_height / 2
                        end_x = x_border + end_col * cell_width_height + cell_width_height / 2
                        end_y = pdf_page_height - y_border - end_row * cell_width_height - cell_width_height / 2
                        self.pdf_canvas.line(start_x, start_y, end_x, end_y)
        
        # Black color for the path line
        self.pdf_canvas.setStrokeColorRGB(0, 0, 0)

        for i in range(grid_height):
            for j in range(grid_width):
                x = x_border + j * cell_width_height
                y = pdf_page_height - y_border - (i + 1) * cell_width_height
                self.pdf_canvas.rect(x, y, cell_width_height, cell_width_height)
                text = str(self.game_pixels[i, j])
                text_width = self.pdf_canvas.stringWidth(text, config['PDF_FONT_NAME'], font_size)
                self.pdf_canvas.drawString(x + (cell_width_height - text_width) / 2, y + (cell_width_height - font_size) / 2, text)
        

    def include_instructions(self):
        if self.do_include_instructions:
            pdf_page_width, pdf_page_height = letter
            max_width = pdf_page_width - 2 * config['PDF_BORDER_WIDTH']

            text_x = config['PDF_BORDER_WIDTH']
            text_y = config['PDF_BORDER_WIDTH'] / 2 + config['PDF_INSTRUCTIONS_HEIGHT']

            specifications_filename = pkg_resources.resource_filename('canvas', 'data/instructions.txt')
            with open(specifications_filename, newline='', encoding='utf-8') as file:
                the_instructions = [line.strip() for line in file.readlines()]

            self.pdf_canvas.setFont(config['PDF_FONT_NAME'], config['PDF_TITLE_FONT_SIZE'])
            self.pdf_canvas.drawString(text_x, text_y, the_instructions[0])

            text_y -= config['PDF_TITLE_FONT_SIZE'] * config['TEXT_LINE_HEIGHT_MULTIPLE']

            self.pdf_canvas.setFont(config['PDF_FONT_NAME'], config['PDF_INSTRUCTIONS_FONT_SIZE'])
            line_height = config['PDF_INSTRUCTIONS_FONT_SIZE'] * config['TEXT_LINE_HEIGHT_MULTIPLE']

            for line in the_instructions[1:]:
                wrapped_lines = self.get_wrapped_text(line, max_width)
                for wrapped_line in wrapped_lines:
                    self.pdf_canvas.drawString(text_x, text_y, wrapped_line)
                    text_y -= line_height
    
    def include_copyright(self):
        self.include_centred_text(config['PDF_COPYRIGHT_TEXT'], config['PDF_COPYRIGHT_FONT_SIZE'], config['PDF_BORDER_WIDTH'] / 2)

    def include_centred_text(self, text, font_size, text_y):
        pdf_page_width, pdf_page_height = letter
        self.pdf_canvas.setFont(config['PDF_FONT_NAME'], font_size)
        text_width = self.pdf_canvas.stringWidth(text, config['PDF_FONT_NAME'], font_size)
        text_x = (pdf_page_width - text_width) / 2
        self.pdf_canvas.drawString(text_x, text_y, text)

    def get_wrapped_text(self, text, max_width):
        words = text.split(' ')
        lines = []
        current_line = ''
        
        for word in words:
            test_line = current_line + word + ' '
            if self.pdf_canvas.stringWidth(test_line) <= max_width:
                current_line = test_line
            else:
                lines.append(current_line.strip())
                current_line = word + ' '
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines