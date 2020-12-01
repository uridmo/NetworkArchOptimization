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
                        self.nodes.insert(i+1, hanger.tie_node)
                        if self.cross_sections:
                            self.cross_sections.insert(i, self.cross_sections[i])
                        break
            else:
                i = self.nodes.index(hanger.tie_node)
        return

    def self_weight(self, first_index=0):
        load_group = super(Tie, self).self_weight(first_index=first_index)
        f_y = -self.weight_deck * self.span / (self.cross_girders_amount+1)
        load_group['Nodal'] = [[node.index, 0, f_y, 0] for node in self.cross_girders_nodes[1:-1]]
        load_group['Nodal'].append([self.cross_girders_nodes[0].index, 0, 1.0*f_y, 0])
        load_group['Nodal'].append([self.cross_girders_nodes[-1].index, 0, 1.0*f_y, 0])
        # load_group['Nodal'].append([self.nodes[0].index, 0, 0.5*f_y, 0])
        # load_group['Nodal'].append([self.nodes[-1].index, 0, 0.5*f_y, 0])
        return load_group

    def weight(self):
        weight = self.weight_deck * self.span
        for i, cross_section in enumerate(self.cross_sections):
            dx = self.nodes[i+1].x - self.nodes[i].x
            g = cross_section.weight
            weight += dx * g
        return weight
