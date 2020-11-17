import numpy as np

from .arch import Arch


class ParabolicArch(Arch):
    def __init__(self, nodes, span, rise, n=30):
        super().__init__(span, rise)

        x_arch = list(np.linspace(0, span, 2 * n + 1))
        y_arch = [rise * (1 - ((x - span/2)/(span/2)) ** 2) for x in x_arch]

        for i in range(len(x_arch)):
            node = nodes.add_node(x_arch[i], y_arch[i])
            self.nodes.append(node)
        return
