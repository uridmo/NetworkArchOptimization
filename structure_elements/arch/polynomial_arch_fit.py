import numpy as np

from structure_elements.arch.arch import Arch


class PolynomialArch(Arch):
    def __init__(self, nodes, arch, n=100):
        span = arch.span
        rise = arch.rise
        super().__init__(nodes, span, rise)

        a = []
        y_ref = []
        c = []
        for node in arch.nodes:
            x = node.x - span/2
            y_ref.append(node.y)
            c.append(rise*(1-(2*x/span)**4))
            a.append([rise*(-(2*x/span)**2 + (2*x/span)**4)])
        a = np.array(a)
        c = np.array(c)
        y_ref = np.array(y_ref)
        b = np.linalg.solve(a.transpose()@a, a.transpose()@(y_ref - c))
        self.b = float(b)

        x_arch = list(np.linspace(0, span, 2 * n + 1))
        y_arch = [float(rise*(1 - b*(2*(x-span/2)/span)**2 - (1-b)*(2*(x-span/2)/span)**4)) for x in x_arch]

        y_2 = np.interp(x_arch, [node.x for node in arch.nodes], [node.y for node in arch.nodes])

        self.d = max(max(y_arch-y_2), -min(y_arch-y_2))


        for i in range(len(x_arch)):
            self.insert_node(nodes, x_arch[i], y_arch[i])
        return
