from structure_elements.line_element import LineElement


class Tie(LineElement):
    def __init__(self, nodes, span, n, g_deck):
        super().__init__()
        self.span = span
        self.cross_girders_amount = n
        self.cross_girders_nodes = [nodes.add_node(span*(i+1)/(n+1), 0) for i in range(n)]
        self.nodes = [nodes.add_node(0, 0)] + self.cross_girders_nodes + [nodes.add_node(span, 0)]
        self.weight_deck = g_deck

    def assign_hangers(self, hangers):
        for hanger in hangers:
            if hanger.tie_node not in self.nodes:
                for i in range(len(self.nodes)-1):
                    if self.nodes[i+1].x > hanger.tie_node.x:
                        break
                self.nodes.insert(i+1, hanger.tie_node)
            else:
                i = self.nodes.index(hanger.tie_node)
        return

    def self_weight(self, first_index=0):
        load_group = super(Tie, self).self_weight(first_index=first_index)
        f_y = -self.weight_deck * self.span / (self.cross_girders_amount+1)
        load_group['Nodal'] = [[node.index, 0, f_y, 0] for node in self.cross_girders_nodes[1:-1]]
        load_group['Nodal'].append([self.cross_girders_nodes[0].index, 0, 1.2*f_y, 0])
        load_group['Nodal'].append([self.cross_girders_nodes[-1].index, 0, 1.2*f_y, 0])
        load_group['Nodal'].append([self.nodes[0].index, 0, 0.3*f_y, 0])
        load_group['Nodal'].append([self.nodes[-1].index, 0, 0.3*f_y, 0])
        return load_group
