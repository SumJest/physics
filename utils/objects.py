import typing
import math


class Vector:
    direction: typing.List[float]

    def __init__(self, length=None, corner=None, direction=None):
        if direction is None:
            self.direction = [length * math.cos(math.radians(corner)), length * math.sin(math.radians(corner))]
        else:
            self.direction = direction

    @staticmethod
    def add(v1, v2):
        # corner = math.radians(abs(v1.direction - v2.direction))
        # length = math.sqrt(abs(v1.length ** 2 + v2.length ** 2 - 2 * v1.length * v2.length * math.cos(corner)))
        # print(length)
        # direction = -math.degrees(math.asin(
        #     (v2.length if (v2.direction % 360) < (v1.direction % 360) else v1.length) * math.sin(
        #         corner) / length)) + max(v1.direction, v2.direction)
        return Vector(direction=[v1.direction[0] + v2.direction[0], v1.direction[1] + v2.direction[1]])

    @staticmethod
    def multiply(v1, number: float):
        return Vector(direction=[v1.direction[0] * number, v1.direction[1] * number])

    @staticmethod
    def multiply_v(v1, v2) -> float:
        return v1.direction[0] * v2.direction[0] + v1.direction[1] * v2.direction[1]

    def __add__(self, other):
        return Vector.add(self, other)

    def __sub__(self, other):
        return Vector.add(self, Vector.multiply(other, -1))

    def __mul__(self, other: typing.Union[float, typing.Any]):
        if type(other) == type(self):
            return Vector.multiply_v(self, other)
        else:
            return Vector.multiply(self, other)

    def __truediv__(self, other: float):
        return Vector.multiply(self, 1 / other)

    def __abs__(self):
        return math.sqrt(self.direction[0] ** 2 + self.direction[1] ** 2)

    def __repr__(self):
        return f"({self.__abs__()}, {self.direction})"

    def len(self, length: float):
        """
        Function sets a new length of vector
        :param length: new length
        :return: None
        """
        self.multiply(self, length / self.__abs__())


class Force(Vector):
    x: float
    y: float

    def __init__(self, x: float, y: float, length=None, corner=None, direction=None):
        super().__init__(length, corner, direction)

        self.x = x
        self.y = y

    def __repr__(self):
        return f"Force({self.__abs__(), self.direction})"


class PhysicObject:
    weight: float
    forces: typing.List[Force]
    id: int = -1
    velocity: Vector

    def __init__(self, weight: float, forces: typing.Union[typing.List[Force], None],
                 velocity: typing.Union[Vector, None]):
        self.forces = []
        self.velocity = Vector(0, 0)
        self.weight = weight
        if forces is not None:
            self.forces = forces
        if velocity is not None:
            self.velocity = velocity


class Body(PhysicObject):
    x: float
    y: float
    size_x: float
    size_y: float
    color: str
    collision: bool = True

    def __init__(self, x: float, y: float, size_x: float, size_y: float, color: str,
                 weight: float, forces: typing.Union[typing.List[Force], None], velocity: typing.Union[Vector, None]):
        self.color = color
        self.size_y = size_y
        self.size_x = size_x
        self.y = y
        self.x = x
        self.forces = []
        self.velocity = Vector(0, 0)
        self.weight = weight
        if forces is not None:
            self.forces = forces
        if velocity is not None:
            self.velocity = velocity


class Wall(PhysicObject):
    x1: float
    x2: float
    y1: float
    y2: float
    color: str
    collision: bool = True

    def __init__(self, x1: float, y1: float, x2: float, y2: float, color: str,
                 forces: typing.Union[typing.List[Force], None] = None):
        self.color = color
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.forces = []
        if forces is not None:
            self.forces = forces


class Line:
    x0: float
    y0: float
    x1: float
    y1: float
    curve: Vector

    def __init__(self, x0: float, y0: float, x1: float, y1: float, curve: Vector):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.curve = curve


class String(PhysicObject):
    lines: typing.List[Line]
    tension: Force
    tied_ids: typing.List[int]

    def __init__(self, lines: typing.List[Line], tension: Force, tied_ids: typing.List[int],  weight: float,
                 forces: typing.Union[typing.List[Force], None],
                 velocity: typing.Union[Vector, None]):
        super().__init__(weight, forces, velocity)
        self.tied_ids = tied_ids
        self.lines = lines
        self.tension = tension
