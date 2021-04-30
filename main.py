import tkinter as tk
import random
import itertools
import math
from iteration_utilities import flatten
from car import Car
from road import Road
from intersection import Intersection
from utils import *

top = tk.Tk()

C = tk.Canvas(top, bg="white", height=size[0], width=size[1])


def genRoad(genLength, currentState=None, pointsOccupied=[], end=None):
    if currentState is None:
        currentState = tuple((e // 200)*100 for e in size)
    # print(currentState, pointsOccupied)
    if end:
        result = pathFind(currentState, stepSize, obstacles=pointsOccupied, end=end)
    else:
        result = pathFind(currentState, stepSize, obstacles=pointsOccupied, length=genLength)
    if result is None:
        print('failed')
        return None
    points = [p.position for p in result]
    return points


# def genRoad(genLength, currentState=None, pointsOccupied=[], end=None):
#     points = [currentState] if currentState else []
#     while len(points) < genLength:
#         newPoint = False
#         repeatCount = 0
#         while (not newPoint) or newPoint in points or newPoint in pointsOccupied or not (
#                 size[0] > newPoint[0] > 0 and size[1] > newPoint[1] > 0):
#             # if their is no valid move undo last move
#             if repeatCount > 100 + ((len(points) == 0) * 1000):
#                 if len(points) > 0:
#                     points.pop()
#                 else:
#                     # no possible valid moves
#                     return None
#             newPoint = tuple(p + (30 * (random.randint(0, 2) - 1)) for p in points[-1]) if len(points) > 0 else (
#                 size[0] / 2, size[1] / 2)
#             repeatCount += 1
#         points.append(newPoint)
#     return points


roads = []
numSegmentsPerRoad = 2
numLights = 30
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
        numSegmentsPerRoad = 5
        allPoints = []
        newSegments = None
        retryCount = 0
    if newSegments is not None:
        newRoad = Road(newSegments, C)
        roads.append(newRoad)
        allPoints += newSegments
    newSegments = genRoad(numSegmentsPerRoad, allPoints[-1] if len(allPoints) > 0 else None, allPoints)
    # no valid moves go back
    if newSegments is None:
        if goBack():
            print('going back one road', len(roads), len(allPoints))

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
