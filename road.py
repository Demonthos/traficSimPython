from line import Line


class Road:
    def __init__(self, points, canvas, color=tuple([0]*3)):
        self.lines = [Line(points[i], points[i + 1], canvas, color=color) for i in range(0, len(points) - 1)]
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
