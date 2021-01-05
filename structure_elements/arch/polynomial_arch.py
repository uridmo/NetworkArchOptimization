import numpy as np

from structure_elements.arch.arch import Arch


class PolynomialArch(Arch):
    def __init__(self, nodes, arch, n=100):
        span = arch.span
        rise = arch.rise
        super().__init__(nodes, span, rise)

        a = []
        b_1 = []
        b_2 = []
        for node in arch.nodes:
            x = node.x - span/2
            y = node.y - rise
            a.append([x**2 - x**4/((span/2)**2)])
            b_1.append(y)
            b_2.append(-rise/((span/2)**4)*(x**4))
        a = np.array(a)
        b_1 = np.array(b_1)
        b_2 = np.array(b_2)
        b = np.linalg.solve(a.transpose()@a, a.transpose()@(b_1 - b_2))
        c = (-rise-b*(span/2)**2)/(span/2)**4
        x_arch = list(np.linspace(0, span, 2 * n + 1))
        y_arch = [float(rise + b*(x-span/2)**2 + c*(x-span/2)**4) for x in x_arch]

        for i in range(len(x_arch)):
            self.insert_node(nodes, x_arch[i], y_arch[i])
        return
