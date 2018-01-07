import math


def sign(x):
    return math.copysign(1, x)


class Point(object):
    def __init__(self, x=None, y=None, coordinates=None):
        if coordinates is not None:
            self.coordinates = coordinates
        else:
            self.coordinates = (x, y)

    @property
    def x(self):
        return self.coordinates[0]

    @property
    def y(self):
        return self.coordinates[1]

    @property
    def distance_to_origin(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __truediv__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return Point(self.x / other, self.y / other)
        else:
            raise TypeError(f'unsupported operand type(s) for /: {type(self).__name__} and {type(other).__name__}')

    def __floordiv__(self, other):
        if isinstance(other, int):
            return Point(self.x // other, self.y // other)
        else:
            raise TypeError(f'unsupported operand type(s) for /: {type(self).__name__} and {type(other).__name__}')

    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return Point(self.x * other, self.y * other)
        else:
            raise TypeError(f'unsupported operand type(s) for /: {type(self).__name__} and {type(other).__name__}')

    def __round__(self, n=None):
        return Point(round(self.x), round(self.y))

    def __repr__(self):
        return f'{type(self).__name__}(x={self.x}, y={self.y})'

    @classmethod
    def euclidean_distance(cls, point1, point2):
        return (point1 - point2).distance_to_origin


class Size(Point):
    @property
    def width(self):
        return self.x

    @property
    def height(self):
        return self.y

    @property
    def shape(self):
        return self.coordinates


class Line(object):
    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2
        self.theta = self.get_theta()

    def get_theta(self):
        point = self.point2 - self.point1
        return math.atan2(point.y, point.x)

    @property
    def rotation(self):
        rotation = self.theta
        if math.fabs(rotation) > math.pi / 2:
            rotation = rotation - sign(rotation) * math.pi

        return math.degrees(rotation)

    @property
    def slope(self):
        m = (self.point2.y - self.point1.y) / (self.point2.x - self.point1.x)
        return m

    @property
    def distance(self):
        return Point.euclidean_distance(self.point1, self.point2)

    def get_equidistant_points(self, percent=0.15):
        point1 = self.point1 * (1 - percent) + self.point2 * percent
        point2 = self.point1 * percent + self.point2 * (1 - percent)
        return round(point1), round(point2)
