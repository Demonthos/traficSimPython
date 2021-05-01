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

C = tk.Canvas(top, bg="white", height=size[0]+20, width=size[1]+20)


def genRoad(genLength, currentState=None, pointsOccupied=[], end=None):
    if currentState is None:
        currentState = tuple(((e // 2) // stepSize)*50 for e in size)
    if end == currentState:
        return None
    if end:
        result = pathFind(currentState, stepSize, obstacles=list(set(pointsOccupied)-set([currentState, end])), end=end)
    else:
        result = pathFind(currentState, stepSize, obstacles=list(set(pointsOccupied)-set([currentState, end])), length=genLength)
    if result is None:
        # print('failed')
        return None
    points = [p.position for p in result]
    return points


roads = []
numSegmentsPerRoad = 2
numRoads = 30
numCars = 50
numInterConnections = 10
allPoints = []
newSegments = None
retryCount = 0


def goBack():
    global allPoints, roads, retryCount
    if len(roads) > 0:
        retryCount += 1
        # recalculate all points
        roads.pop().delete(C)
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


while len(roads) < numRoads:
    # retried a lot
    if retryCount > 500:
        while len(roads) > 0:
            roads.pop().delete(C)
        numSegmentsPerRoad = 5
        allPoints = []
        newSegments = None
        retryCount = 0
        print('resetting')
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

while numInterConnections > 0:
    road1 = random.choice(roads)
    road2 = None
    tryCount = 0
    while (road2 is None or road1 == road2 or chebyshevDistance(road1.lines[0].point1, road2.lines[0].point1) > 4*stepSize) and tryCount < 100:
        road2 = random.choice(roads)
        tryCount += 1
    newSegments = genRoad(numSegmentsPerRoad, road1.lines[0].point1, allPoints, end=road2.lines[0].point1)
    if newSegments is not None:
        if DEBUG:
            newRoad = Road(newSegments, C, color=(255, 0, 0))
        else:
            newRoad = Road(newSegments, C)
        roads.append(newRoad)
        allPoints += newSegments
        boolVal = True
        new = boolVal not in road1.connected.keys()
        intersection = road1.connected[boolVal] if not new else Intersection(20)
        newRoad.addConnection(intersection, C, boolVal)
        if new:
            road1.addConnection(intersection, C, boolVal)
        boolVal = True
        new = boolVal not in road2.connected.keys()
        intersection = road2.connected[boolVal] if not new else Intersection(20)
        newRoad.addConnection(intersection, C, not boolVal)
        if new:
            road2.addConnection(intersection, C, boolVal)
        # print('added inter connection')
        numInterConnections -= 1
    else:
        # print('failed to added inter connection')
        # print(road1.lines[0].point1, road2.lines[0].point1)
        pass

cars = [Car((100, 100), 10, C) for i in range(numCars)]
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
