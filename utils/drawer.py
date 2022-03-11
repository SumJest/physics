import typing
from datetime import datetime
from tkinter import Tk, Canvas, Frame, ALL
from utils.objects import Vector, Body, Force, Wall, String, Line  # , String
import math


class Cons:
    BOARD_WIDTH = 800
    BOARD_HEIGHT = 800
    DELAY = 1


class Board(Canvas):
    bodys: typing.List[typing.Union[Body, Wall, String]]
    last_time: float
    is_pause: bool = False

    def __init__(self):
        super().__init__(
            width=Cons.BOARD_WIDTH, height=Cons.BOARD_HEIGHT,
            background="white", highlightthickness=0
        )
        self.initSim()
        self.pack()

    def draw_vector(self, vector: Vector, x: float, y: float, fill: str):
        self.create_line(x, y, x + vector.direction[0], y + vector.direction[1], arrow="last", fill=fill, tags="vector")

    def doPhysic(self):
        time_now = datetime.now().timestamp()
        for body in self.bodys:
            # body.x += velocity * (time_now - self.last_time) * math.cos(math.radians(body.momentum.direction))

            if type(body) == Body:
                addition = (body.velocity * (time_now - self.last_time))
                body.x += addition.direction[0]
                body.y += addition.direction[1]
                resultant = Vector(0, 0)
                for force in body.forces:
                    resultant += force
                body.velocity += resultant / body.weight

    def draw(self):
        for body in self.bodys:

            if body.id == -1:
                if type(body) == Body:
                    body.id = self.create_rectangle(body.x, body.y, body.x + body.size_x, body.y + body.size_y,
                                               fill=body.color, tags="body")
                elif type(body) == Wall:
                    body.id = self.create_line(body.x1, body.y1, body.x2, body.y2,
                                               fill=body.color, tags="body")
                elif type(body) == String:
                    for line in body.lines:
                        self.create_line(line.x0, line.y0, line.x1, line.y1, fill="black")
            else:

                if type(body) == Body:
                    self.moveto(body.id, body.x, body.y)
                    self.draw_vector(body.velocity, body.x + body.size_x // 2, body.y + body.size_y // 2,
                                     fill=body.color)
                    for force in body.forces:
                        self.draw_vector(force * 5, body.x + body.size_x // 2, body.y + body.size_y // 2,
                                         fill="red")


    def getBodyIById(self, id: int) -> int:
        for i in range(len(self.bodys)):
            if self.bodys[i].id == id:
                return i

    def turn_on_coolision(self, body_id: int):
        self.bodys[body_id].collision = True

    def mkcollision(self, b1: int, b2: int):
        body1 = self.getBodyIById(b1)
        body2 = self.getBodyIById(b2)
        if not self.bodys[body1].collision or not self.bodys[body2].collision:
            return
        v1 = (2 * abs(self.bodys[body2].velocity) * self.bodys[body2].weight + abs(self.bodys[body1].velocity) * (self.bodys[body1].weight - self.bodys[body2].weight)) / (self.bodys[body1].weight + self.bodys[body2].weight)
        v2 = (2 * abs(self.bodys[body1].velocity) * self.bodys[body1].weight + abs(self.bodys[body2].velocity) * (self.bodys[body2].weight - self.bodys[body1].weight)) / (self.bodys[body1].weight + self.bodys[body2].weight)
        vb1 = self.bodys[body1].velocity
        vb2 = self.bodys[body2].velocity
        # self.draw_vector(self.bodys[body1].velocity, 100, 200, fill=self.bodys[body1].color)
        # self.draw_vector(self.bodys[body2].velocity, 100, 200, fill=self.bodys[body2].color)
        n1 = Vector(direction=[self.bodys[body1].x - self.bodys[body2].x, self.bodys[body1].y - self.bodys[body2].y])
        n2 = Vector(direction=[self.bodys[body2].x - self.bodys[body1].x, self.bodys[body2].y - self.bodys[body1].y])
        self.bodys[body1].velocity = (vb1 - (n1 * 2) * ((vb1 * n1) / (n1 * n1)))
        self.bodys[body2].velocity = (vb2 - (n2 * 2) * ((vb2 * n2) / (n2 * n2)))
        self.bodys[body1].velocity.len(v1)
        self.bodys[body2].velocity.len(v2)
        self.draw_vector(self.bodys[body1].velocity, self.bodys[body1].x + 10, self.bodys[body1].y + 10, fill=self.bodys[body1].color)
        self.draw_vector(self.bodys[body2].velocity, self.bodys[body2].x + 10, self.bodys[body2].y + 10, fill=self.bodys[body2].color)
        #self.is_pause = True
        self.bodys[body1].collision = False

        self.bodys[body2].collision = False
        self.after(100, self.turn_on_coolision, body1)
        self.after(100, self.turn_on_coolision, body2)
        pass

    def makeCollisionWithWall(self, b: int, w: int):
        body = self.bodys[self.getBodyIById(b)]
        wall = self.bodys[self.getBodyIById(w)]
        if not body.collision or not wall.collision:
            return
        v = abs(body.velocity)
        n = Vector(direction=[wall.y1 - wall.y2, wall.x2 - wall.x1])
        self.draw_vector(n, body.x, body.y, wall.color)
        body.velocity = (body.velocity - (n * 2) * ((body.velocity * n) / (n * n)))
        body.velocity.len(v)
        body.collision = False
        self.after(100, self.turn_on_coolision, self.getBodyIById(b))
        #self.is_pause = True

    def checkCollisions(self):
        collisions = []
        for body in self.bodys:
            if type(body) == String:
                continue
            for ovr in self.find_overlapping(*self.bbox(body.id)):

                if ovr == body.id:
                    continue
                if "body" not in self.gettags(ovr):
                    continue
                if {body.id, ovr} in collisions:
                    continue
                if type(body) != Body:
                    continue
                if type(self.bodys[self.getBodyIById(ovr)]) == Wall:
                    #self.makeCollisionWithWall(body.id, ovr)
                    body.velocity.direction[1] *= 0
                    # if len(body.forces) < 4:
                    #     body.forces.append(body.forces[0] * -1)
                    #     f = Force(10, 10, direction=(body.velocity * -1).direction)
                    #     f.len(abs(body.forces[1]) * 0.1)
                    #     body.forces.append(f)
                    #     body.forces.append(f*5)
                    # else:

                    body.forces[1] = body.forces[0] * -1
                    f = Force(10, 10, direction=(body.velocity * -1).direction)
                    #f.len(abs(body.forces[1]) * 0.1)
                    f *= abs(body.forces[1] * 0.1) / abs(f)
                    body.forces[2] = f
                    continue
                if type(self.bodys[self.getBodyIById(ovr)]) == Body:
                    self.mkcollision(body.id, ovr)
                    collisions.append({body.id, ovr})

    def onTimer(self):
        self.delete("vector")
        self.draw()
        self.doPhysic()
        self.checkCollisions()

        self.last_time = datetime.now().timestamp()
        if not self.is_pause:
            self.after(Cons.DELAY, self.onTimer)

    def initSim(self):
        self.bodys = []
        self.last_time = datetime.now().timestamp()
        self.bodys.append(Body(350, 280, 50, 20, "#1f1", 4, forces=[Force(10, 10, 4*10, 90), Force(10, 10, 0, 0), Force(10, 10, 0, 0), Force(10, 0, 0, 0)], velocity=Vector(0, 0)))

        self.bodys.append(Wall(300, 300, 700, 300, "black"))
        self.bodys.append(Body(300, 350, 10, 10, "red", 1, forces=[Force(10, 10, 1 * 10, 90), Force(10, 10, 0, 0)],
                               velocity=None))
        self.bodys.append(Body(700, 350, 14, 14, "red", 2, forces=[Force(10, 10, 2 * 10, 90), Force(10, 10, 0, 0)],
                               velocity=None))
        self.bodys.append(String([Line(300,300,300, 350, Vector(direction=[0, 1])), Line(300, 300, 350, 280, Vector(direction=[0,1]))],
                                 Force(10,10,0,0), [0, 2], 0, None, None))
        self.bodys.append(String([Line(700, 300, 400, 280, Vector(direction=[0, 1])), Line(700, 300, 700, 350, Vector(direction=[0, 1]))],
                                 Force(10,10,0,0), [0, 2], 0, None, None))
        # self.bodys.append(Body(237, 209, 20, 20, "#1ff", 1, forces=[], velocity=Vector(0, 120)))
        # v1 = Vector(50, 80)
        # v2 = Vector(100, 120)
        #
        # self.draw_vector(v1, 200, 200, "#1f1")
        # self.draw_vector(v2, 200 + v1.direction[0] - v2.direction[0], 200 + v1.direction[1] - v2.direction[1], "#1ff")
        # self.draw_vector(v1 - (v2 * 2) * ((v1 * v2) / (v2 * v2)), 200 + v1.direction[0],  200 + v1.direction[1], "#f1f")
        self.after(Cons.DELAY, self.onTimer)


class Example(Frame):

    def __init__(self):
        super().__init__()
        self.master.title("ФИЗИКа")
        self.board = Board()
        self.pack()


def main():
    root = Tk()
    ex = Example()
    root.geometry(f"{Cons.BOARD_WIDTH}x{Cons.BOARD_HEIGHT}")
    root.mainloop()
