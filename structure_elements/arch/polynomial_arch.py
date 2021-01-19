import numpy as np

from .arch import Arch


class QuarticArch(Arch):
    def __init__(self, nodes, span, rise, b, n=100):
        super().__init__(nodes, span, rise)

        x_arch = list(np.linspace(0, span, 2 * n + 1))
        y_arch = [rise*(1 - b*(2*(x-span/2)/span)**2 - (1-b)*(2*(x-span/2)/span)**4) for x in x_arch]

        for i in range(len(x_arch)):
            self.insert_node(nodes, x_arch[i], y_arch[i])
        return
