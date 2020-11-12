from warnings import warn

import numpy as np

from .hangers import Hangers


class RadialHangerSet(Hangers):
    def __init__(self, nodes, span, rise, beta, n, skip=0):
        super().__init__()
        radius = (rise ** 2 + (span / 2) ** 2) / (2 * rise)
        diag = (rise ** 2 + (span / 2) ** 2) ** 0.5
        alpha = np.arcsin((diag / 2) / radius)

        # Calculate angle of inclination of the arch
        angles_0 = np.linspace(-2 * alpha, 2 * alpha, num=2 * (n + 1 + skip)).tolist()
        angles_0 = angles_0[2 + skip:-1 - skip:2]
        angles_1 = list(map(lambda x: np.pi / 2 - x - beta, angles_0))

        pos_arch_x = [radius * np.sin(angles_0[i]) for i in range(n)]
        pos_arch_y = [rise - radius + radius * np.cos(angles_0[i]) for i in range(n)]

        pos_tie_x = [span / 2 + pos_arch_x[i] - pos_arch_y[i] / np.tan(angles_1[i]) for i in range(n)]

        # Check whether the hangers do not cross each other
        checks = [pos_tie_x[i] > pos_tie_x[i + 1] for i in range(n - 1)]
        if any(checks):
            warn("Some hangers cross each other")

        # Check whether all hangers lie on the tie
        kicks = 0
        for i in range(n):
            if pos_tie_x[i - kicks] < 0:
                pos_tie_x.pop(i - kicks)
                angles_1.pop(i - kicks)
                kicks += 1
                warn("The " + str(i) + ". hanger of the set was deleted as it lies outside the tie")

        for i in range(len(angles_1)):
            self.add_hanger(nodes, pos_tie_x[i], angles_1[i])
        return
