import numpy as np
from scipy.interpolate import splrep, splev

from structure_elements.arch.arch import Arch


class SplineArch(Arch):
    def __init__(self, nodes, arch, hangers, n=100):
        # arch.arch_connection_nodes(nodes, hangers)

        span = arch.span
        rise = arch.rise
        super().__init__(nodes, span, rise)

        xy = [(0, 0), (span/2, rise), (span, 0)]
        for hanger in hangers:
            xy.append((hanger.arch_node.x, hanger.arch_node.y))
        sorted_xy = sorted(xy, key=lambda tup: tup[0])
        x = [node[0] for node in sorted_xy]
        y = [node[1] for node in sorted_xy]

        tck = splrep(x, y, s=0)
        x_arch = list(np.linspace(0, span, 2 * n + 1))
        y_arch = splev(x_arch, tck, der=0)

        for i in range(len(x_arch)):
            self.insert_node(nodes, x_arch[i], y_arch[i])
        return
