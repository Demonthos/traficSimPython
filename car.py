import random
from utils import DEBUG, _from_rgb


class Car:
    def __init__(self, position, size, canvas, color=(255, 0, 0)):
        self.size = size
        self.obj = canvas.create_oval(position[0], position[1], position[0] - size, position[1] - size, width=2,
                                      fill=_from_rgb(color))

    def move(self, point, canvas):
        canvas.move(self.obj, point[0], point[1])

    def moveTo(self, point, canvas):
        canvas.moveto(self.obj, point[0], point[1])

    def drive(self, line, currentDelay, canvas, forward=True, stopEarly=0, removeCar=True, startEarly=0):
        canvas.after(currentDelay, lambda: line.addCar(self, canvas))
        newLength = line.length - stopEarly - startEarly
        lengthOfLine = int(newLength)
        sizeOffset = [self.size / 2] * 2
        movement = (line.xLength * (newLength / line.length),
                    (newLength / line.length) * line.yLength)
        startingPos = tuple(e1 + e2 for e1, e2 in zip(line.point1,
                                                      (e * (startEarly if forward else stopEarly) / lengthOfLine for e
                                                       in movement)))
        for i in (range(0, lengthOfLine) if forward else range(lengthOfLine - 1, -1, -1)):
            newPos = [((i / lengthOfLine) * m) + p - s for m, p, s in
                      zip(movement, startingPos, sizeOffset)]
            canvas.after(currentDelay, self.moveTo, newPos, canvas)
            currentDelay += 10
            # print(newPos)
        if removeCar:
            canvas.after(currentDelay, lambda: line.removeCar(self, canvas))
        return currentDelay

    def getCarsInFront(self, road, forward, line):
        intersection = road.connected[not forward]
        k = list(intersection.waitingCallbacks.keys())
        if self in k:
            k = k[:k.index(self)]
        carsInLine = set(k) & set(line.carsOn)
        return carsInLine

    def changeRoad(self, currentRoad, canvas, forward=True, stoppedEarly=0):
        # remove self from last line and find next road
        allLines = (currentRoad.lines if forward else currentRoad.lines[::-1])
        if (not forward) in currentRoad.connected.keys():
            currentIntersection = currentRoad.connected[not forward]
            newRoad = random.choice(list(currentIntersection.roads - set([currentRoad])))
            connected = newRoad.connected
            newRoadForward = list(connected.keys())[list(connected.values()).index(currentIntersection)]

            def updatePos(moveIn):
                nonlocal stoppedEarly
                line = allLines[-1]
                inFront = self.getCarsInFront(currentRoad, forward, line)
                stopEarlyDist = sum((e.size for e in inFront))
                if not moveIn:
                    stopEarlyDist += currentIntersection.size / 2
                start = line.length - stoppedEarly
                # print(len(inFront))
                if int(line.length - start - stopEarlyDist) != 0:
                    self.drive(line, 0, canvas, forward, startEarly=start, stopEarly=stopEarlyDist, removeCar=moveIn)
                stoppedEarly = stopEarlyDist

            def whenFinished():
                self.follow(newRoad, canvas, newRoadForward)

            currentIntersection.wait(self, updatePos, whenFinished, canvas)
        else:
            if DEBUG:
                print('looping back')
            self.follow(currentRoad, canvas, not forward)
        # print(currentRoad.connected, forward)

    def follow(self, road, canvas, forward=True):
        currentDelay = 0
        allLines = (road.lines if forward else road.lines[::-1])
        allButLastLine = allLines[:-1]
        for line in allButLastLine:
            currentDelay = self.drive(line, currentDelay, canvas, forward)
        nextCallback = lambda stopEarlyDist: self.changeRoad(road, canvas, forward, stopEarlyDist)
        line = allLines[-1]
        if len(allLines) > 0 and (not forward) in road.connected.keys():
            def currentCallback():
                intersection = road.connected[not forward]
                # print(carsInLine, stopEarlyDist)

                def lambdaFunc():
                    stopEarlyDist = (intersection.size / 2) + sum(
                        (e.size for e in self.getCarsInFront(road, forward, line)))
                    if line.length - stopEarlyDist > 1:
                        currentDelay = self.drive(line, 0, canvas, forward, stopEarly=stopEarlyDist, removeCar=False)
                        canvas.after(currentDelay, nextCallback, stopEarlyDist)
                    else:
                        canvas.after(100, lambdaFunc)

                lambdaFunc()

        else:
            def currentCallback():
                stopEarlyDist = 0
                currentDelay = self.drive(line, 0, canvas, forward)
                canvas.after(currentDelay, nextCallback, stopEarlyDist)
        canvas.after(currentDelay, currentCallback)
