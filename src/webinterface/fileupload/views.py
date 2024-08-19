from django.shortcuts import render
from django.http import HttpResponse
from .forms import UploadFileForm
from reportlab.pdfgen import canvas
from PIL import Image
from django.http import JsonResponse

from game.game import Game
from .utils import convert_image_to_pdf, create_zip_archive

    
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            filename = request.FILES['filename']
            difficulty = form.cleaned_data['difficulty']
            grid_size_int = form.cleaned_data['grid_size']
            puzzle_title = form.cleaned_data['puzzle_title']
            do_include_instructions = form.cleaned_data['do_include_instructions']
            show_solution = form.cleaned_data['show_solution']

            # Map the image_size slider value to actual sizes
            size_map = {
                '1': 'small',
                '2': 'medium',
                '3': 'large'
            }
            grid_size = size_map.get(grid_size_int, 'small')

            pdf_io, pdf_io_solution = convert_image_to_pdf(filename, difficulty, grid_size, puzzle_title, do_include_instructions)
            pdf_filename = f'{puzzle_title}.pdf'

            if show_solution:
                pdfs = [(pdf_io, pdf_filename), (pdf_io_solution, f'{puzzle_title} (solution).pdf')]
                zip_buffer = create_zip_archive(pdfs)
            
                response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename="{puzzle_title}" (with solution).zip'
            else:
                response = HttpResponse(pdf_io, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'

            return response
    else:
        form = UploadFileForm()

    return render(request, 'upload.html', {'form': form})
