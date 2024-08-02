from src.numberjoiner.Colour import Colour

def test_colour():
    assert Colour.White != Colour.Grey
    assert Colour.Grey != Colour.Red
    assert Colour.White != Colour.Red