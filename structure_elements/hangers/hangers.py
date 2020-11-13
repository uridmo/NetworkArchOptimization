from copy import deepcopy
from math import ceil

import numpy as np

from .hanger import Hanger
from ..effects import multiply_effect
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

    def add_hanger(self, nodes, x_tie, angle):
        node = nodes.add_node(x_tie, 0)
        hanger = Hanger(node, angle)
        self.hangers.append(hanger)
        return

    def set_stiffness(self, ea, ei):
        for hanger in self.hangers:
            hanger.axial_stiffness = ea
            hanger.bending_stiffness = ei
        return

    def get_beams(self, indices):
        n = len(self)
        beams_nodes = [[self.hangers[i].tie_node.index, self.hangers[i].arch_node.index] for i in range(n)]
        beams_stiffness = []
        for i in range(n):
            stiffness = [self.hangers[i].axial_stiffness, self.hangers[i].bending_stiffness]
            beams_stiffness.append(stiffness)
        beams_releases = [[i, 1, 1] for i in indices]
        return beams_nodes, beams_stiffness, beams_releases

    def set_effects(self, effects, name, key=None):
        super(Hangers, self).set_effects(effects, name, key=key)
        if not key:
            for i in range(len(self)):
                self.hangers[i].effects_N[name] = effects['Normal Force'][i][0]
        elif key == 'Normal Force':
            for i in range(len(self)):
                self.hangers[i].effects_N[name] = effects[i][0]
        return

    def get_range(self, range_name, name=''):
        range_new = super(Hangers, self).get_range(range_name, name=name)
        if name:
            for i in range(len(self)):
                if name not in self.hangers[i].effects_range_N:
                    self.hangers[i].effects_range_N[name] = {}
                self.hangers[i].effects_range_N[name]['Max'] = range_new['Max']['Normal Force'][i][0]
                self.hangers[i].effects_range_N[name]['Min'] = range_new['Min']['Normal Force'][i][0]
        return range_new

    def assign_permanent_effects(self, key=None):
        if not key:
            self.assign_permanent_effects('Normal Force')
            self.assign_permanent_effects('Shear Force')
            self.assign_permanent_effects('Moment')
            effects = self.get_effects('Permanent')
            self.set_effects(multiply_effect(effects, 0), '0')
        else:
            effects = []
            for hanger in self.hangers:
                n = ceil(hanger.length())+1
                if key == 'Normal Force':
                    effects.append([hanger.prestressing_force for i in range(n)])
                else:
                    effects.append([0 for i in range(n)])
            self.set_effects(effects, 'Permanent', key=key)
        return

    def plot_elements(self, ax):
        for hanger in self.hangers:
            x = [hanger.tie_node.x, hanger.arch_node.x]
            y = [hanger.tie_node.y, hanger.arch_node.y]
            ax.plot(x, y, color='black', linewidth=1)
        return

    def plot_internal_forces(self):

        return
