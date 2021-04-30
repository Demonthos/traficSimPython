import tkinter as tk
import random
import itertools
import math
from iteration_utilities import flatten

size = [500] * 2


def _from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    r, g, b = rgb
    return f'#{r:02x}{g:02x}{b:02x}'


class Car:
    def __init__(self, position, size, canvas):
        self.size = size
        self.obj = canvas.create_oval(position[0], position[1], position[0] - size, position[1] - size, width=2,
                                      fill='red')

    def move(self, point, canvas):
        canvas.move(self.obj, point[0], point[1])

    def moveTo(self, point, canvas):
        canvas.moveto(self.obj, point[0], point[1])

    def drive(self, line, currentDelay, canvas, forward=True):
        canvas.after(currentDelay, lambda: line.addCar(self, canvas))
        lengthOfLine = int(line.length)
        startingPos = line.point1
        sizeOffset = [self.size / 2] * 2
        movement = (line.xLength, line.yLength)
        for i in (range(0, lengthOfLine) if forward else range(lengthOfLine, 0, -1)):
            newPos = [((i / lengthOfLine) * m) + p - s for m, p, s in
                      zip(movement, startingPos, sizeOffset)]
            canvas.after(currentDelay, self.moveTo, newPos, canvas)
            currentDelay += 10
            # print(newPos)
        canvas.after(currentDelay, lambda: line.removeCar(self, canvas))
        return currentDelay

    def changeRoad(self, currentRoad, canvas, forward=True):
        if (not forward) in currentRoad.connected.keys():
            currentIntersection = currentRoad.connected[not forward]
            callback = lambda: self.follow(random.choice(list(currentIntersection.roads - set([currentRoad]))), canvas,
                                           forward)
            currentIntersection.wait(callback, canvas)
        else:
            self.follow(currentRoad, canvas, not forward)
        # print(currentRoad.connected, forward)

    def follow(self, road, canvas, forward=True):
        currentDelay = 0
        for line in (road.lines if forward else road.lines[::-1]):
            currentDelay = self.drive(line, currentDelay, canvas, forward)
        canvas.after(currentDelay, self.changeRoad, road, canvas, forward)


class Line:
    def __init__(self, point1, point2, canvas):
        self.point1: tuple = point1
        self.point2: tuple = point2
        self.obj = canvas.create_line(point1[0], point1[1], point2[0], point2[1], width=10)
        self.carsOn: set = set()
        self.updateColor(canvas)

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
        return self.yLength / self.xLength

    def updateColor(self, canvas):
        canvas.itemconfig(self.obj, fill=_from_rgb((10 * len(self.carsOn), 0, 0)))

    def addCar(self, car, canvas):
        self.carsOn.add(car)
        self.updateColor(canvas)

    def removeCar(self, car, canvas):
        self.carsOn.remove(car)
        self.updateColor(canvas)

    def delete(self, canvas):
        canvas.delete(self.obj)


class Road:
    def __init__(self, points, canvas):
        self.lines = [Line(points[i], points[i + 1], canvas) for i in range(0, len(points) - 1)]
        self.connected_ = {}

    @property
    def carsOn(self):
        total = set()
        for line in self.lines:
            total |= line.carsOn
        return total

    def addConnection(self, intersection, canvas, start=True):
        self.connected_[start] = intersection
        intersection.addConnection(self, canvas, start)

    @property
    def connected(self):
        return self.connected_

    def delete(self, canvas):
        for line in self.lines:
            line.delete(canvas)


class Intersection:
    def __init__(self, size):
        self.size = size
        self.roads = set()
        self.obj = None
        self.objPos = None
        self.clearIntersectionTime = 300
        self.waiting = []

    def getRandom(self):
        return random.choice(list(self.roads))

    def updateColor(self, canvas):
        if self.obj:
            canvas.itemconfig(self.obj, fill=_from_rgb((min(255, 100 * len(self.waiting)), 0, 255)))

    def addConnection(self, road, canvas, start):
        position = road.lines[0].point1 if start else road.lines[-1].point2
        position = [p + (self.size / 2) for p in position]
        if self.objPos != position:
            if self.obj:
                canvas.itemconfig(self.obj, fill='red')
            self.obj = canvas.create_oval(position[0], position[1], position[0] - self.size, position[1] - self.size,
                                      width=2,
                                      fill='red' if self.obj else 'blue')
            self.objPos = position
        self.roads.add(road)
        # print(position, self.roads, start, road.connected)

    def resolveWaitingCallbacks(self, canvas):
        self.updateColor(canvas)
        if len(self.waiting) > 0:
            self.resolveCallback(self.waiting[-1], canvas)

    def resolveCallback(self, callback, canvas):
        canvas.after(self.clearIntersectionTime, callback)
        # you must remove before resolving waiting callbacks to avoid errors
        canvas.after(self.clearIntersectionTime, lambda c: (self.waiting.remove(callback), self.resolveWaitingCallbacks(c)), canvas)

    def wait(self, callback, canvas):
        self.waiting.append(callback)
        if len(self.waiting) <= 1:
            self.resolveWaitingCallbacks(canvas)


top = tk.Tk()

C = tk.Canvas(top, bg="white", height=size[0], width=size[1])


def genRoad(genLength, currentState=None, pointsOccupied=[]):
    points = [currentState] if currentState else []
    while len(points) <= genLength:
        newPoint = False
        repeatCount = 0
        while (not newPoint) or newPoint in points or newPoint in pointsOccupied or not (
                size[0] > newPoint[0] > 0 and size[1] > newPoint[1] > 0):
            # if their is no valid move undo last move
            if repeatCount > 100 + ((len(points) == 0) * 1000):
                if len(points) > 0:
                    points.pop()
                else:
                    # no possible valid moves
                    return None
            newPoint = tuple(p + (30 * (random.randint(0, 2) - 1)) for p in points[-1]) if len(points) > 0 else (
                size[0] / 2, size[1] / 2)
            repeatCount += 1
        points.append(newPoint)
    return points


numSegmentsPerRoad = 3
numLights = 60
roads = []
allPoints = [None]
newSegments = None
retryCount = 0


def goBack():
    global allPoints, roads, retryCount
    retryCount += 1
    if len(roads) > 0:
        # recalculate all points
        roads[-1].delete(C)
        roads.pop(-1)
        allPoints = list(flatten(flatten([[(line.point1, line.point2) for line in road.lines] for road in roads])))
        pPoint = None
        newAllPoints = []
        for point in allPoints:
            if (not pPoint) or point != pPoint:
                newAllPoints.append(point)
            pPoint = point
        allPoints = newAllPoints
        return True
    else:
        return False


while len(roads) < numLights:
    # retried a lot
    if retryCount > 500:
        while len(roads) > 0:
            roads.pop().delete(C)
        allPoints = [None]
        newSegments = None
        retryCount = 0
    if newSegments is not None:
        newRoad = Road(newSegments, C)
        roads.append(newRoad)
        allPoints += newSegments
    newSegments = genRoad(numSegmentsPerRoad, allPoints[-1], allPoints)
    # no valid moves go back
    if newSegments is None:
        print('before going back:', len(roads), len(allPoints))
        if goBack():
            print('after going back one road', len(roads), len(allPoints))
        else:
            print('returned false')

pRoad = None
for road in roads:
    if pRoad:
        intersection = Intersection(20)
        road.addConnection(intersection, C, True)
        pRoad.addConnection(intersection, C, False)
    pRoad = road
cars = [Car((100, 100), 10, C) for i in range(1, 30)]
for i, car in enumerate(cars):
    if i % 2 == 0:
        car.follow(roads[random.randint(0, len(roads) - 1)], C, True)
    else:
        car.follow(roads[random.randint(0, len(roads) - 1)], C, False)


def move(event):
    # change visualization mode here
    pass


top.bind("<Key>", move)

C.pack()
top.mainloop()
