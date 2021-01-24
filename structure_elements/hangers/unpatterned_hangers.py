import numpy as np
from .hanger_set import HangerSet


class UnpatternedHangerSet(HangerSet):
    def __init__(self, nodes, span, angles):
        super().__init__()
        n = len(angles)
        for i in range(n):
            x_tie = span * (i+1)/(n+1)
            if angles[i] == 90:
                angle = np.radians(89.5)
            else:
                angle = np.radians(angles[i])

            self.add_hanger(nodes, x_tie, angle)
        return
