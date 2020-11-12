from copy import deepcopy

import numpy as np

from .hanger import Hanger
from ..element import Element


def mirror_hanger_set(nodes, hanger_set, span):
    hangers = deepcopy(hanger_set)
    for hanger in hanger_set.hangers:
        x_tie = span - hanger.tie_node.x
        angle = np.pi - hanger.inclination
        hangers.add_hanger(nodes, x_tie, angle)
    hangers.hangers.sort(key=lambda h: h.tie_node.x)
    return hangers


class Hangers(Element):
    def __init__(self):
        super().__init__()
        self.hangers = []
        self.impacts_N = {}
        self.impacts_range_N = {}
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

    def beams(self, indices):
        n = len(self)
        beams_nodes = [[self.hangers[i].tie_node.index, self.hangers[i].arch_node.index] for i in range(n)]
        beams_stiffness = []
        for i in range(n):
            stiffness = [self.hangers[i].axial_stiffness, self.hangers[i].bending_stiffness]
            beams_stiffness.append(stiffness)
        beams_releases = [[i, 1, 1] for i in indices]
        return beams_nodes, beams_stiffness, beams_releases

    def set_impacts_n(self):

        return

    def plot_effects(self):

        return

    def plot_effects_range(self):

        return
