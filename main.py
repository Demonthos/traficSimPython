import tkinter as tk
import random
import itertools
import math


class Car:
    def __init__(self, position, size, canvas):
        self.obj = canvas.create_oval(position[0], position[1], size, size, width=2, fill='red')

    def move(self, point, canvas):
        canvas.move(self.obj, point[0], point[1])

    def moveTo(self, point, canvas):
        canvas.moveto(self.obj, point[0], point[1])

    def follow(self, road, canvas):
        currentDelay = 0
        for line in road.lines:
            lengthOfLine = line.length
            movement = ((line.xLength/lengthOfLine)+line.point1[0], (line.yLength/lengthOfLine)+line.point1[1])
            print(movement)
            for i in range(0, int(lengthOfLine)):
                canvas.after(currentDelay, self.moveTo, [e*i for e in movement], canvas)
                currentDelay += 10


class Line:
    def __init__(self, point1, point2, canvas):
        self.point1 = point1
        self.point2 = point2
        self.obj = canvas.create_line(point1[0], point1[1], point2[0], point2[1], width=2, fill='red')

    @property
    def xLength(self):
        return self.point2[0] - self.point1[0]

    @property
    def yLength(self):
        return self.point2[1] - self.point1[1]

    @property
    def length(self):
        return math.sqrt(self.xLength ** 2 + self.yLength ** 2)

    @property
    def slope(self):
        return self.yLength/self.xLength


class Road:
    def __init__(self, lines):
        self.lines = lines


top = tk.Tk()

C = tk.Canvas(top, bg="white", height=500, width=500)

# points = (0, 0), (0, 100), (100, 0)
# image = C.create_polygon(list(itertools.chain(*points)))
car = Car((100, 100), 20, C)
road = Road([Line((0, 0), (300, 300), C), Line((300, 300), (100, 200), C), Line((100, 200), (400, 300), C)])
car.follow(road, C)


def move(event):
    car.move((random.randint(-10, 10), random.randint(-10, 10)), C)


top.bind("<Key>", move)

C.pack()
top.mainloop()
