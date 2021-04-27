import tkinter as tk
import random
import itertools
import math


class Car:
    def __init__(self, position, size, canvas):
        self.obj = canvas.create_oval(position[0], position[1], size, size, width=2, fill='red')

    def move(self, point, canvas):
        canvas.move(self.obj, point[0], point[1])

    def follow(self, road, canvas):
        for line in road.lines:
            lengthOfLine = int(math.sqrt((line.point1[0] - line.point2[0])**2 + (line.point1[1] - line.point2[1])**2))
            for i in range(0, lengthOfLine):
                positionInLine = (i/lengthOfLine)*(line.point2[1] - line.point1[1])
                print(positionInLine)
                slope = (line.point1[1] - line.point2[1])/(line.point1[0] - line.point2[0])
                position = (positionInLine - line.point1[1], slope*(positionInLine - line.point1[0]))
                canvas.after(100*i, self.move, position, canvas)


class Line:
    def __init__(self, point1, point2, canvas):
        self.point1 = point1
        self.point2 = point2
        self.obj = canvas.create_line(point1[0], point1[1], point2[0], point2[1], width=2, fill='red')


class Road:
    def __init__(self, lines, canvas):
        self.lines = lines


top = tk.Tk()

C = tk.Canvas(top, bg="white", height=500, width=500)

# points = (0, 0), (0, 100), (100, 0)
# image = C.create_polygon(list(itertools.chain(*points)))
car = Car((100, 100), 20, C)
road = Road([Line((0, 0), (300, 300), C)], C)
car.follow(road, C)


def move(event):
    car.move((random.randint(-10, 10), random.randint(-10, 10)), C)


top.bind("<Key>", move)

C.pack()
top.mainloop()
