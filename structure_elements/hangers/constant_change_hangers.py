from .hanger_set import HangerSet


class ConstantChangeHangerSet(HangerSet):
    def __init__(self, nodes, span, n, angle_0, angle_mid):
        super().__init__()
        da = angle_0 - angle_mid
        for i in range(n):
            x_tie = span * (i+1)/(n+1)
            angle = angle_mid - da * (2 * x_tie - span) / span
            self.add_hanger(nodes, x_tie, angle)
        return
