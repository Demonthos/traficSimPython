import random
from utils import _from_rgb
from collections import OrderedDict


class Intersection:
    def __init__(self, size):
        self.size = size
        self.roads = set()
        self.obj = None
        self.objPos = None
        self.clearIntersectionTime = 1000
        self.waitingCallbacks = OrderedDict()
        self.color = 'green'

    def getRandom(self):
        return random.choice(list(self.roads))

    def updateColor(self, canvas):
        if self.obj:
            canvas.itemconfig(self.obj, fill=_from_rgb((min(255, 100 * len(self.waitingCallbacks)),
                                                        100 * (self.color == 'green'), 255 * (self.color == 'blue'))))

    def addConnection(self, road, canvas, start):
        position = road.lines[0].point1 if start else road.lines[-1].point2
        position = [p + (self.size / 2) for p in position]
        if self.objPos != position:
            if self.obj:
                canvas.itemconfig(self.obj, fill=self.color)
                self.color = 'blue'
                print('DUPLICATE INTERSECTION')
            self.obj = canvas.create_oval(position[0], position[1], position[0] - self.size, position[1] - self.size,
                                          width=2,
                                          fill=self.color)
            self.updateColor(canvas)
            self.objPos = position
        self.roads.add(road)
        # print(position, self.roads, start, road.connected)

    def updateCars(self, nextCar):
        for k in self.waitingCallbacks.keys():
            onUpdate, onFinish = self.waitingCallbacks[k]
            onUpdate(nextCar == k)

    def resolveWaitingCallbacks(self, canvas):
        if len(self.waitingCallbacks) > 0:
            nextCar = list(self.waitingCallbacks.keys())[0]
        else:
            nextCar = None
        self.updateCars(nextCar)
        if nextCar:
            self.resolveCallback(nextCar, canvas)
        self.updateColor(canvas)

    def resolveCallback(self, car, canvas):
        canvas.after(self.clearIntersectionTime, self.waitingCallbacks[car][1])
        # you must remove before resolving waitingCallbacks callbacks to avoid errors
        canvas.after(self.clearIntersectionTime,
                     lambda c: (self.waitingCallbacks.pop(car), self.resolveWaitingCallbacks(c)), canvas)

    def wait(self, car, onUpdate, onFinish, canvas, currentDelay=0):
        if len(self.waitingCallbacks) > 0:
            nextCar = list(self.waitingCallbacks.keys())[0]
        else:
            nextCar = None
        self.updateCars(nextCar)
        canvas.after(currentDelay, self._wait, car, onUpdate, onFinish, canvas)

    def _wait(self, car, onUpdate, onFinish, canvas):
        self.waitingCallbacks[car] = onUpdate, onFinish
        if len(self.waitingCallbacks) <= 1:
            self.resolveWaitingCallbacks(canvas)
