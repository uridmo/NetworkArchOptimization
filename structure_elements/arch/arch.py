import numpy as np

from structure_elements.line_element import LineElement


class Arch(LineElement):
    def __init__(self, nodes, span, rise):
        super().__init__()
        self.span = span
        self.rise = rise
        self.nodes = [nodes.add_node(0, 0), nodes.add_node(span, 0)]
        self.tie_tension = None
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

    def define_by_peak_moment(self, nodes, hangers, mz_0, peak_moment=0):
        self.assign_permanent_effects(nodes, hangers, 0, -mz_0)
        moments_arch = self.effects['Permanent']['Moment']
        moment_max = max(moments_arch)
        n_0 = (moment_max - peak_moment) / self.rise
        self.tie_tension = n_0
        return n_0
