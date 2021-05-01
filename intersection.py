import random
from utils import _from_rgb


class Intersection:
    def __init__(self, size):
        self.size = size
        self.roads = set()
        self.obj = None
        self.objPos = None
        self.clearIntersectionTime = 300
        self.waiting = []
        self.color = 'green'

    def getRandom(self):
        return random.choice(list(self.roads))

    def updateColor(self, canvas):
        if self.obj:
            canvas.itemconfig(self.obj, fill=_from_rgb((min(255, 100 * len(self.waiting)), 100*(self.color == 'green'), 255*(self.color == 'blue'))))

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

    def resolveWaitingCallbacks(self, canvas):
        self.updateColor(canvas)
        if len(self.waiting) > 0:
            self.resolveCallback(self.waiting[-1], canvas)

    def resolveCallback(self, callback, canvas):
        canvas.after(self.clearIntersectionTime, callback)
        # you must remove before resolving waiting callbacks to avoid errors
        canvas.after(self.clearIntersectionTime,
                     lambda c: (self.waiting.remove(callback), self.resolveWaitingCallbacks(c)), canvas)

    def wait(self, callback, canvas):
        self.waiting.append(callback)
        if len(self.waiting) <= 1:
            self.resolveWaitingCallbacks(canvas)
