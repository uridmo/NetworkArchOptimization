import numpy as np

from structure_elements.line_element import LineElement


class Arch(LineElement):
    def __init__(self, span, rise):
        super().__init__()
        self.span = span
        self.rise = rise
        return

    def arch_connection_nodes(self, nodes, hangers):
        for hanger in hangers:
            x_tie = hanger.tie_node.x
            angle = hanger.inclination

            for i in range(len(self.nodes) - 1):
                x_arch_1 = self.nodes[i].x
                x_arch_2 = self.nodes[i+1].x
                y_arch_1 = self.nodes[i].y
                y_arch_2 = self.nodes[i+1].y
                dx = x_arch_2 - x_arch_1
                dy = y_arch_2 - y_arch_1
                if angle == np.pi / 2:
                    if x_arch_1 < x_tie < x_arch_2:
                        x = x_tie
                        y = y_arch_1 + dy * (x_tie - x_arch_1) / dx
                        node = self.insert_node(nodes, x, y)
                        hanger.arch_node = node
                        break
                else:
                    tan_a = np.tan(angle)
                    a = -(dy * tan_a * x_tie - dy * tan_a * x_arch_1 + dx * tan_a * y_arch_1) / (dy - dx * tan_a)
                    b = -(y_arch_1 - tan_a * x_arch_1 + tan_a * x_tie) / (dy - dx * tan_a)
                    if -10**-10 <= b < 1:
                        x = x_arch_1 + b * dx
                        y = y_arch_1 + b * dy
                        node = self.insert_node(nodes, x, y)
                        hanger.arch_node = node
                        break
        return
