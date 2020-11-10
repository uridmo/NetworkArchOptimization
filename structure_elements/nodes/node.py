class Node:
    def __init__(self, i, x, y):
        self.index = i
        self.x = x
        self.y = y

    def __repr__(self):
        string = f'i:' + str(self.index)
        string += ',(' + str(round(self.x, 3))
        string += ',' + str(round(self.y, 3)) + ')'
        return string

    def __eq__(self, other):
        return self.index == other.index

    def coordinates(self):
        node = [self.x, self.y]
        return node
