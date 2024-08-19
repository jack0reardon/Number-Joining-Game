from django import forms

from config.config import Config

config = Config()

class UploadFileForm(forms.Form):
    filename = forms.FileField(label='Choose an image')
    difficulty = forms.IntegerField(
        label="Difficulty",
        widget=forms.NumberInput(attrs={'type': 'range', 'min': '1', 'max': '10', 'step': '1'}),
        initial=5
    )
    grid_size = forms.ChoiceField(
        label="Grid Size",
        choices=[
            ('1', 'Small'),
            ('2', 'Medium'),
            ('3', 'Large')
        ],
        widget=forms.NumberInput(attrs={'type': 'range', 'min': '1', 'max': '3', 'step': '1', 'value': '1'}),
        initial='1'
    )
    puzzle_title = forms.CharField(
        label="Puzzle Title",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter Puzzle Title'})
    )
