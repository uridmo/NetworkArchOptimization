import numpy as np
from copy import deepcopy
from .hanger import Hanger


def mirror_hanger_set(nodes, hanger_set, span):
    hangers = deepcopy(hanger_set)
    for hanger in hanger_set.hangers:
        x_tie = span - hanger.tie_node.x
        angle = np.pi - hanger.inclination
        hangers.add_hanger(nodes, x_tie, angle)
    hangers.hangers.sort(key=lambda h: h.tie_node.x)
    return hangers


class Hangers:
    def __init__(self):
        self.hangers = []
        self.axial_stiffness = None
        self.bending_stiffness = None
        return

    def __repr__(self):
        return repr(self.hangers)

    def __len__(self):
        return len(self.hangers)

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if self.i < len(self):
            result = self.hangers[self.i]
            self.i += 1
            return result
        else:
            raise StopIteration

    def add_hanger(self, nodes, x_tie, angle, i=None):
        node = nodes.add_node(x_tie, 0)
        hanger = Hanger(node, angle)
        self.hangers.append(hanger)
        return

    def assign_stiffness(self, ea, ei):
        for hanger in self.hangers:
            hanger.axial_stiffness = ea
            hanger.bending_stiffness = ei
        return

    def get_beams(self, indices):
        n = len(self)
        beams_nodes = [[self.hangers[i].tie_node.index, self.hangers[i].arch_node.index] for i in range(n)]
        beams_stiffness = n * [[self.axial_stiffness, self.bending_stiffness]]
        beams_releases = [[i, 1, 1] for i in indices]
        return beams_nodes, beams_stiffness, beams_releases

    # def self_weight_loads(self, indices):
    #     n = len(self)
    #     q = self.weight
    #     load_distributed = [[i, 0, 0, 0, -q, 0, 0, -q, 0] for i in indices]
    #     return load_distributed
