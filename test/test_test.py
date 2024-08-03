from game.game import Game

def test_game():
    the_game = Game('C:/Users/sexy0/Documents/Python/mona-lisa.jpg', width_in_pxls_max = 20, height_in_pxls_max = 20)
    print(the_game)
    assert False