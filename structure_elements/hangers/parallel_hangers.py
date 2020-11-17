from .hanger_set import HangerSet


class ParallelHangerSet(HangerSet):
    def __init__(self, nodes, span, n, angle):
        super().__init__()

        for i in range(n):
            x_tie = span * (i+1)/(n+1)
            self.add_hanger(nodes, x_tie, angle)
        return
