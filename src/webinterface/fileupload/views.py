from django.shortcuts import render
from django.http import HttpResponse
from .forms import UploadFileForm
from reportlab.pdfgen import canvas
from PIL import Image
from django.http import JsonResponse

from game.game import Game
from .utils import convert_image_to_pdf

    
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            filename = request.FILES['filename']
            difficulty = form.cleaned_data['difficulty']
            grid_size_int = form.cleaned_data['grid_size']
            puzzle_title = form.cleaned_data['puzzle_title']

            # Map the image_size slider value to actual sizes
            size_map = {
                '1': 'small',
                '2': 'medium',
                '3': 'large'
            }
            grid_size = size_map.get(grid_size_int, 'small')

            pdf_io = convert_image_to_pdf(filename, difficulty, grid_size, puzzle_title)
            response = HttpResponse(pdf_io, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{puzzle_title}.pdf"'
            return response
    else:
        form = UploadFileForm()

    return render(request, 'upload.html', {'form': form})
