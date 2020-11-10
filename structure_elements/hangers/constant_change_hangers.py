from .hangers import Hangers


class ConstantChangeHangerSet(Hangers):
    def __init__(self, nodes, span, angle_0, angle_mid, n):
        super().__init__()
        da = angle_0 - angle_mid
        for i in range(n):
            x_tie = span * (i+1)/(n+1)
            angle = angle_mid - da * (2 * x_tie - span) / span
            self.add_hanger(nodes, x_tie, angle)
        return
