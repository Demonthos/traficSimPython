import random


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