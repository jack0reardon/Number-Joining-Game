from src.image import GreyscaleImage
from src.numberjoiner import Colour

def test_colour():
    assert Colour.White != Colour.Grey
    assert Colour.Grey != Colour.Red
    assert Colour.White != Colour.Red