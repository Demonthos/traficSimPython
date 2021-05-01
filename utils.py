from sortedcontainers import SortedSet
import random

size = [700] * 2
stepSize = 50
DEBUG = False


def _from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    r, g, b = rgb
    return f'#{r:02x}{g:02x}{b:02x}'


def chebyshevDistance(position1, position2):
    return max(abs(position1[0] - position2[0]), abs(position1[1] - position2[1]))


def pathFind(start, stepDist, obstacles=[], maxSize=size, minSize=(0, 0), end=None, length=None):
    if length and end:
        raise TypeError("can't accept both end and length")

    def getNeighbors(position):
        permutations = (1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1), (-1, 1), (1, -1)
        # print(position, stepDist)
        values = [tuple(c + (stepDist * p) for c, p in zip(position, permutation)) for permutation in permutations]
        newValues = []
        for value in values:
            if minSize[1] <= value[0] <= maxSize[0] and minSize[1] <= value[1] <= maxSize[1]:
                newValues.append(value)
        return newValues

    class Node:
        def __init__(self, position, previous, timeToNode=0):
            self.position = position
            self.previous = previous
            self.timeToNode = timeToNode

        @property
        def score(self):
            if end:
                return self.timeToNode + chebyshevDistance(self.position, end.position)
            else:
                return self.timeToNode + random.randint(-1, 1)

        def getPathTo(self):
            path = [self]
            while path[-1].previous:
                path.append(path[-1].previous)
            return list(reversed(path))

        def __hash__(self):
            return hash(self.position)

    start = Node(start, None)
    if end:
        end = Node(end, None)
    openSet = SortedSet([start], key=lambda e: e.score)
    closedSet = SortedSet(key=lambda e: e.score)

    while len(openSet) > 0:
        bestChoice = openSet.pop(0)
        if (length is not None and len(bestChoice.getPathTo()) > length) or (
                end is not None and bestChoice.position == end.position):
            # print('success')
            return bestChoice.getPathTo()
        for pos in getNeighbors(bestChoice.position):
            newNode = Node(pos, bestChoice, bestChoice.timeToNode + 1)
            if newNode.position not in obstacles and newNode.position not in (e.position for e in closedSet):
                inOpenSet = None
                for node in openSet:
                    if node.position == newNode.position:
                        inOpenSet = node
                        break
                if not inOpenSet:
                    openSet.add(newNode)
                elif newNode.timeToNode < inOpenSet.timeToNode:
                    inOpenSet.timeToNode = newNode.timeToNode
                    inOpenSet.previous = bestChoice
        closedSet.add(bestChoice)
        # print(len(openSet))
        # print(len(closedSet))
        # print(bestChoice.position)
        # print()
    return None


if __name__ == '__main__':
    print([e.position for e in pathFind((250, 300), 50, [(250, 250), (300, 250), (350, 250), (350, 300), (300, 300), (250, 350), (250, 350), (200, 350), (150, 350), (100, 350), (100, 350), (100, 400), (100, 450), (150, 500), (150, 500), (200, 450), (250, 500), (300, 450), (300, 450), (250, 400), (300, 350), (200, 300), (150, 250), (100, 300), (100, 300), (50, 250), (100, 200), (50, 150), (50, 150), (100, 100), (100, 50), (150, 0), (150, 0), (200, 50), (250, 50), (300, 50)], end=(400, 250))])
