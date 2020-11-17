from structure_elements.line_element import LineElement


class Tie(LineElement):
    def __init__(self, nodes, span):
        super().__init__()
        self.nodes = [nodes.add_node(0, 0)] + [nodes.add_node(span, 0)]

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
