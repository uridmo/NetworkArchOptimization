from .hangers import Hangers


class ParallelHangerSet(Hangers):
    def __init__(self, nodes, span, angle, n):
        super().__init__()

        for i in range(n):
            x_tie = span * (i+1)/(n+1)
            self.add_hanger(nodes, x_tie, angle)
        return
