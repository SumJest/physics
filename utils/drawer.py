import typing
from datetime import datetime
from tkinter import Tk, Canvas, Frame, ALL, Button
from utils.objects import Vector, Body, Force, Wall, String, Line, Cursor  # , String
import math


class Cons:
    BOARD_WIDTH = 800
    BOARD_HEIGHT = 800
    DELAY = 1
    colors = ["green", "blue"]
    gravity = 0
    G = 10


class Board(Canvas):
    bodies: typing.List[typing.Union[Body, Wall, String]]
    start_time: float
    last_time: float
    is_pause: bool = False
    cursor: Cursor
    acceleration: float
    text_timer: int

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
        self.acceleration = (abs(self.bodies[2].getresultant()) - abs(self.bodies[1].getresultant()) - abs(self.bodies[0].getresultant())) / \
                            (self.bodies[2].weight + self.bodies[1].weight + self.bodies[0].weight)
        for body in self.bodies:
            if type(body) == Body:
                body.move(time_now - self.last_time)
                body.velocity += Vector(length=self.acceleration * (time_now - self.last_time), corner=body.direction)

                body.forces["gravity"] = Force(10, 10, Cons.G * body.weight, 90)
            # if type(body) == String:
            #     body.tension = self.bodies[body.tied_ids[0]].weight * (self.acceleration + Cons.G)
            #     for


    def draw(self):
        for body in self.bodies:

            if body.id == -1:
                if type(body) == Body:
                    body.id = self.create_rectangle(body.x, body.y, body.x + body.size_x, body.y + body.size_y,
                                                    fill=body.color, tags="body")
                elif type(body) == Wall:
                    body.id = self.create_line(body.x1, body.y1, body.x2, body.y2,
                                               fill=body.color, tags="body")
                # elif type(body) == String:
                #     for line in body.lines:
                #         self.create_line(line.x0, line.y0, line.x1, line.y1, fill="black")
            else:

                if type(body) == Body:
                    self.moveto(body.id, body.x, body.y)

        if self.cursor.id == -1:
            self.cursor.id = self.create_text(self.cursor.x, self.cursor.y, text=f"({self.cursor.x}, {self.cursor.y})")
        else:
            self.itemconfig(self.cursor.id, text=f"({self.cursor.x}, {self.cursor.y})")
            self.moveto(self.cursor.id, self.cursor.x, self.cursor.y)
        self.itemconfig(self.text_timer,
                        text=datetime.fromtimestamp(self.last_time - self.start_time).strftime("%M:%S.%f")[:-3])

    def getBodyIById(self, id: int) -> int:
        for i in range(len(self.bodies)):
            if self.bodies[i].id == id:
                return i

    def turn_on_coolision(self, body_id: int):
        self.bodies[body_id].collision = True

    def mkcollision(self, b1: int, b2: int):
        body1 = self.getBodyIById(b1)
        body2 = self.getBodyIById(b2)
        if not self.bodies[body1].collision or not self.bodies[body2].collision:
            return
        v1 = (2 * abs(self.bodies[body2].velocity) * self.bodies[body2].weight + abs(self.bodies[body1].velocity) * (
                self.bodies[body1].weight - self.bodies[body2].weight)) / (
                     self.bodies[body1].weight + self.bodies[body2].weight)
        v2 = (2 * abs(self.bodies[body1].velocity) * self.bodies[body1].weight + abs(self.bodies[body2].velocity) * (
                self.bodies[body2].weight - self.bodies[body1].weight)) / (
                     self.bodies[body1].weight + self.bodies[body2].weight)
        vb1 = self.bodies[body1].velocity
        vb2 = self.bodies[body2].velocity
        # self.draw_vector(self.bodys[body1].velocity, 100, 200, fill=self.bodys[body1].color)
        # self.draw_vector(self.bodys[body2].velocity, 100, 200, fill=self.bodys[body2].color)
        n1 = Vector(
            direction=[self.bodies[body1].x - self.bodies[body2].x, self.bodies[body1].y - self.bodies[body2].y])
        n2 = Vector(
            direction=[self.bodies[body2].x - self.bodies[body1].x, self.bodies[body2].y - self.bodies[body1].y])
        self.bodies[body1].velocity = (vb1 - (n1 * 2) * ((vb1 * n1) / (n1 * n1)))
        self.bodies[body2].velocity = (vb2 - (n2 * 2) * ((vb2 * n2) / (n2 * n2)))
        self.bodies[body1].velocity.len(v1)
        self.bodies[body2].velocity.len(v2)
        # self.draw_vector(self.bodies[body1].velocity, self.bodies[body1].x + 10, self.bodies[body1].y + 10,
        #                  fill=self.bodies[body1].color)
        # self.draw_vector(self.bodies[body2].velocity, self.bodies[body2].x + 10, self.bodies[body2].y + 10,
        #                  fill=self.bodies[body2].color)
        # self.is_pause = True
        self.bodies[body1].collision = False

        self.bodies[body2].collision = False
        self.after(100, self.turn_on_coolision, body1)
        self.after(100, self.turn_on_coolision, body2)
        pass

    def makeCollisionWithWall(self, b: int, w: int):

        body = self.bodies[self.getBodyIById(b)]
        wall = self.bodies[self.getBodyIById(w)]
        if not body.collision or not wall.collision:
            return
        v = abs(body.velocity)
        n = Vector(direction=[wall.y1 - wall.y2, wall.x2 - wall.x1])
        # self.draw_vector(n, body.x, body.y, wall.color)
        body.velocity = (body.velocity - (n * 2) * ((body.velocity * n) / (n * n)))
        body.velocity.len(v)
        body.collision = False
        self.after(100, self.turn_on_coolision, self.getBodyIById(b))

    def checkCollisions(self):
        collisions = []
        for body in self.bodies:
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
                if type(self.bodies[self.getBodyIById(ovr)]) == Wall:
                    wall = self.bodies[self.getBodyIById(ovr)]
                    n = Vector(direction=[wall.y1 - wall.y2, wall.x2 - wall.x1])

                    v1 = (body.velocity * n) / abs(n)

                    n *= v1 / abs(n)

                    # self.draw_vector(n, body.x, body.y, fill="blue")
                    # self.makeCollisionWithWall(body.id, ovr)

                    body.velocity -= n

                    # if len(body.forces) < 4:
                    #     body.forces.append(body.forces[0] * -1)
                    #     f = Force(10, 10, direction=(body.velocity * -1).direction)
                    #     f.len(abs(body.forces[1]) * 0.1)
                    #     body.forces.append(f)
                    #     body.forces.append(f*5)
                    # else:
                    body.forces["normal"] = body.forces["gravity"] * -1
                    f = Force(10, 10, direction=(body.velocity * -1).direction)
                    # f.len(abs(body.forces[1]) * 0.1)
                    if abs(f) != 0:
                        f *= abs(body.forces["normal"] * 0.1) / abs(f)

                    body.forces["friction"] = f
                    continue
                if type(self.bodies[self.getBodyIById(ovr)]) == Body:
                    self.mkcollision(body.id, ovr)
                    collisions.append({body.id, ovr})

    def onMotion(self, event):
        self.cursor.x, self.cursor.y = event.x, event.y

    def pause(self):
        self.is_pause = not self.is_pause
        print(1)

    def reset_timer(self):
        self.start_time = self.last_time

    def onTimer(self):
        if not self.is_pause:

            self.delete("vector")
            self.draw()
            self.doPhysic()
            self.checkCollisions()
        else:
            self.start_time += datetime.now().timestamp() - self.last_time
        self.last_time = datetime.now().timestamp()




        self.after(Cons.DELAY, self.onTimer)
            # self.is_pause = True

    def initSim(self):
        self.bodies = []
        self.last_time = datetime.now().timestamp()
        self.start_time = self.last_time
        str_timer = datetime.fromtimestamp(self.last_time - self.start_time).strftime("%M:%S.%f")[:-3]
        self.text_timer = self.create_text(30, Cons.BOARD_HEIGHT-10, text=str_timer)

        ButtonPause = Button(self, width=10, text="??????????", command=self.pause)
        ButtonReset = Button(self, width=10, text="????????????????", command=self.reset_timer)

        self.create_window((160,  Cons.BOARD_HEIGHT), anchor="sw", window=ButtonPause)
        self.create_window((60, Cons.BOARD_HEIGHT), anchor="sw", window=ButtonReset)

        self.bodies.append(Body(350, 280, 50, 20, "#1f1", 4,
                                forces={},
                                velocity=Vector(0, 0),
                                direction=0))

        self.bodies.append(Body(300, 700, 10, 10, "red", 1,
                                forces={},
                                velocity=None,
                                direction=-90))
        self.bodies.append(Body(700, 350, 14, 14, "red", 2,
                                forces={},
                                velocity=None,
                                direction=90))
        self.bodies.append(Wall(300, 300, 700, 300, "black"))

        # self.bodies.append(Wall(300, 300, 300, 100, "black"))
        # self.bodies.append(Wall(700, 300, 700, 100, "black"))
        # self.bodys.append(Body(237, 209, 20, 20, "#1ff", 1, forces=[], velocity=Vector(0, 120)))
        # v1 = Vector(50, 80)
        # v2 = Vector(100, 120)
        #
        # self.draw_vector(v1, 200, 200, "#1f1")
        # self.draw_vector(v2, 200 + v1.direction[0] - v2.direction[0], 200 + v1.direction[1] - v2.direction[1], "#1ff")
        # self.draw_vector(v1 - (v2 * 2) * ((v1 * v2) / (v2 * v2)), 200 + v1.direction[0],  200 + v1.direction[1], "#f1f")
        self.bind("<Motion>", self.onMotion)
        self.cursor = Cursor(0, 0)
        self.after(Cons.DELAY, self.onTimer)


class Example(Frame):

    def __init__(self):
        super().__init__()
        self.master.title("????????????")
        self.board = Board()
        self.pack()


def main():
    root = Tk()
    ex = Example()
    root.geometry(f"{Cons.BOARD_WIDTH}x{Cons.BOARD_HEIGHT}")
    root.mainloop()

