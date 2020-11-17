from copy import deepcopy
from math import ceil

import numpy as np

from .hanger import Hanger
from ..effects import multiply_effect
from ..element import Element


def mirror_hanger_set(nodes, hanger_set, span):
    hanger_set_mirrored = deepcopy(hanger_set)
    for hanger in hanger_set_mirrored:
        hanger.tie_node = nodes.add_node(span - hanger.tie_node.x, 0)
        hanger.inclination = np.pi - hanger.inclination
    hanger_set_mirrored.hangers.sort(key=lambda h: h.tie_node.x)
    hangers = [hanger_set, hanger_set_mirrored]
    return hangers


class HangerSet:
    def __init__(self):
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


class Hangers(Element):
    def __init__(self, nodes, hanger_set, span):
        super().__init__()
        self.hanger_sets = mirror_hanger_set(nodes, hanger_set, span)
        return

    def __len__(self):
        length = 0
        for hanger_set in self.hanger_sets:
            length += len(hanger_set)
        return length

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if self.i < len(self):
            i = self.i
            j = 0
            while i >= len(self.hanger_sets[j]):
                j += 1
                i -= len(self.hanger_sets[j])
            result = self.hanger_sets[j].hangers[i]
            self.i += 1
            return result
        else:
            raise StopIteration

    def define_cross_section(self, cross_section):
        for hanger in self:
            hanger.cross_section = cross_section
        return

    def get_beams(self, indices):
        n = len(self)
        beams_nodes = []
        beams_stiffness = []
        for hanger in self:
            beams_nodes.append([hanger.tie_node.index, hanger.arch_node.index])
            beams_stiffness.append(hanger.get_beam())
        beams_releases = [[i, 1, 1] for i in indices]
        return beams_nodes, beams_stiffness, beams_releases

    def set_effects(self, effects, name, key=None):
        super(Hangers, self).set_effects(effects, name, key=key)
        if not key:
            for i, hanger in enumerate(self):
                hanger.effects_N[name] = effects['Normal Force'][i][0]
        elif key == 'Normal Force':
            for i, hanger in enumerate(self):
                hanger.effects_N[name] = effects[i][0]
        return

    def get_range(self, range_name, name=''):
        range_new = super(Hangers, self).get_range(range_name, name=name)
        if name:
            for i, hanger in enumerate(self):
                if name not in hanger.effects_range_N:
                    hanger.effects_range_N[name] = {}
                hanger.effects_range_N[name]['Max'] = range_new['Max']['Normal Force'][i][0]
                hanger.effects_range_N[name]['Min'] = range_new['Min']['Normal Force'][i][0]
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
            for hanger in self:
                n = ceil(hanger.length()) + 1
                if key == 'Normal Force':
                    effects.append([hanger.prestressing_force for i in range(n)])
                else:
                    effects.append([0 for i in range(n)])
            self.set_effects(effects, 'Permanent', key=key)
        return

    def plot_elements(self, ax):
        for hanger in self:
            x = [hanger.tie_node.x, hanger.arch_node.x]
            y = [hanger.tie_node.y, hanger.arch_node.y]
            ax.plot(x, y, color='black', linewidth=0.7)
        return

    def plot_internal_forces(self):

        return