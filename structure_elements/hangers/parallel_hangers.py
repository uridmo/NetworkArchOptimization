from .hanger_set import HangerSet


class ParallelHangerSet(HangerSet):
    def __init__(self, nodes, span, n, angle, spaced=False, dead_zone=0.0):
        super().__init__()
        s = 2 if spaced else 1
        span_eff = span - 2*dead_zone
        for i in range(n):
            x_tie = dead_zone + span_eff * (s*i+1)/(s*n+1)
            self.add_hanger(nodes, x_tie, angle)
        return
