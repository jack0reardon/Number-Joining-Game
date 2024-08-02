from collections import namedtuple

Point = namedtuple('Point', 'x y')

def get_point_within_border(greyscale_image, x, y):
    width, height = greyscale_image.greyscale_grid.shape
    return Point(max(0, min(x, width - 1)), max(0, min(y, height - 1)))

def get_point_N(greyscale_image, point):
    return get_point_within_border(greyscale_image, point.x, point.y - 1)

def get_point_S(greyscale_image, point):
    return get_point_within_border(greyscale_image, point.x, point.y + 1)

def get_point_E(greyscale_image, point):
    return get_point_within_border(greyscale_image, point.x + 1, point.y)

def get_point_W(greyscale_image, point):
    return get_point_within_border(greyscale_image, point.x - 1, point.y)

get_points_NSEW = [get_point_N, get_point_S, get_point_E, get_point_W]