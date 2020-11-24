from copy import deepcopy

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

    def plot_effects(self, ax, name, key='', label='', c='black', lw=1.0, ls='-'):
        x = []
        n = []
        if not key:
            if type(self.hangers[0].effects_N[name]) is not dict:
                for hanger in self:
                    x.append(hanger.tie_node.x)
                    n.append(hanger.effects_N[name]/1000)
                ax.plot(x, n, label=label, c=c, lw=lw, ls=ls)
            else:
                self.plot_effects(ax, name, key='Max', label=label, c=c, lw=lw, ls=ls)
                self.plot_effects(ax, name, key='Min', label=label, c=c, lw=lw, ls=ls)
        else:
            for hanger in self:
                x.append(hanger.tie_node.x)
                n.append(hanger.effects_N[name][key]/1000)
            ax.plot(x, n, label=label, c=c, lw=lw, ls=ls, marker="x")
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

    def set_effects(self, effects, name):
        if type(effects) is dict:
            if type(effects['Normal Force']) is list:
                effects_i = np.array([effects['Normal Force'][i][0] for i in range(len(self))])
            else:
                effects_i = effects['Normal Force']
        elif type(effects) is list:
            effects_i = np.array([effects[i][0] for i in range(len(self))])
        self.effects[name] = {'Normal Force': effects_i}
        for i, hanger in enumerate(self):
            if effects_i.ndim == 1:
                hanger.effects_N[name] = effects_i[i]
            else:
                hanger.effects_N[name] = effects_i[:, i]
        return

    def set_prestressing_forces(self, forces):
        forces_list = list(forces)
        forces_list = forces_list + forces_list[::-1]
        for i, hanger in enumerate(self):
            hanger.prestressing_force = forces_list[i]
        return

    def get_hanger_forces(self, i=None):
        hanger_forces = []
        if type(i) is int:
            for hanger in self.hanger_sets[i]:
                hanger_forces.append(hanger.prestressing_force)
        else:
            for hanger in self:
                hanger_forces.append(hanger.prestressing_force)
        return hanger_forces

    def assign_permanent_effects(self):
        effects = []
        for hanger in self:
            effects.append([hanger.prestressing_force])
        self.set_effects(effects, 'Permanent')
        effects = self.get_effects('Permanent')
        self.set_effects(multiply_effect(effects, 0), '0')
        return

    def plot_elements(self, ax):
        for hanger in self:
            x = [hanger.tie_node.x, hanger.arch_node.x]
            y = [hanger.tie_node.y, hanger.arch_node.y]
            ax.plot(x, y, color='black', linewidth=0.7)
        return

    def plot_effects(self, ax, name, label='', c='black', lw=1.0, ls='-'):
        n = len(self.hanger_sets[0])
        effects = self.get_effects(name)['Normal Force']
        if effects.ndim == 1:
            values = effects[0:n]
        else:
            values = effects[:, 0:n]
        tie_node_x = [hanger.tie_node.x for hanger in self.hanger_sets[0]]
        ax.plot(tie_node_x, values.transpose()/1000, label=label, c=c, lw=lw, ls=ls)
        return
