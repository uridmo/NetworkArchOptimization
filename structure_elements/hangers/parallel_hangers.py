from .hanger_set import HangerSet


class ParallelHangerSet(HangerSet):
    def __init__(self, nodes, span, n, angle, spaced=False):
        super().__init__()
        s = 2 if spaced else 1
        for i in range(n):
            x_tie = span * (s*i+1)/(s*n+1)
            self.add_hanger(nodes, x_tie, angle)
        return
