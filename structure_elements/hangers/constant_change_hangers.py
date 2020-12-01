from .hanger_set import HangerSet


class ConstantChangeHangerSet(HangerSet):
    def __init__(self, nodes, span, n, angle_0, angle_mid, spaced=False):
        super().__init__()
        da = angle_0 - angle_mid
        s = 2 if spaced else 1
        for i in range(n):
            x_tie = span * (s*i+1)/(s*n+1)
            angle = angle_mid - da * (2 * x_tie - span) / span
            self.add_hanger(nodes, x_tie, angle)
        return
