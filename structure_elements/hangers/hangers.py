import numpy as np

from .hanger_set import HangerSet
from ..effects import multiply_effect
from ..element import Element


class Hangers(Element):
    def __init__(self, nodes, hanger_set, span):
        super().__init__()
        self.hanger_sets = hanger_set.mirror(nodes, span)
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
                i -= len(self.hanger_sets[j])
                j += 1
            result = self.hanger_sets[j].hangers[i]
            self.i += 1
            return result
        else:
            raise StopIteration

    def assign_cross_section(self, cross_section):
        for hanger in self:
            hanger.cross_section = cross_section
        return

    def assign_length_to_cross_section(self):
        for hanger in self:
            hanger.cross_section.length += hanger.length()
        return

    def assign_range_to_sections(self, name):
        for i, hanger in enumerate(self):
            hanger.cross_section.assign_extrema(hanger.effects_N[name], name, 'Normal Force')
            hanger.cross_section.calculate_doc_max(name, is_hanger=True)
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

    def get_connection_points(self):
        nodes_all = [hanger.tie_node for hanger in self]
        nodes = []
        for node in nodes_all:
            if node not in nodes:
                nodes.append(node)
        x_coord = [node.x for node in nodes]
        return x_coord, nodes

    def get_max_connection_forces(self):
        nodes = self.get_connection_points()[1]
        forces = [0] * len(nodes)
        for hanger in self:
            for i in range(len(nodes)):
                if nodes[i] == hanger.tie_node:
                    forces[i] += np.sin(hanger.inclination) * hanger.cross_section.normal_force_resistance
        return forces

    def set_prestressing_force_from_nodes(self, nodes, forces):
        for i in range(len(forces)):
            sine_sum = 0
            for hanger in self:
                if hanger.tie_node == nodes[i]:
                    sine_sum += np.sin(hanger.inclination)
            hanger_force = forces[i] / sine_sum
            for hanger in self:
                if hanger.tie_node == nodes[i]:
                    hanger.prestressing_force = hanger_force
        return

    def set_effects(self, effects, name, key=None):
        if type(effects) is dict:
            if type(effects['Normal Force']) is list:
                effects_i = np.array([effects['Normal Force'][i][0] for i in range(len(self))])
            else:
                effects_i = effects['Normal Force']
        elif type(effects) is list:
            if type(effects[0]) is list:
                effects_i = np.array([effects[i][0] for i in range(len(self))])
            elif len(effects) == 1:
                effects_i = np.array([effects[0] for i in range(len(self))])
            else:
                effects_i = np.array([effects for i in range(len(self))]).transpose()
        else:
            raise Exception('Unknown input format.')

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

    def define_knuckles(self, nodes, span, tie, arch, mz_0, cs_knuckle, knuckle_x, knuckle_inclination):
        knuckle = HangerSet()
        knuckle.add_hanger(nodes, knuckle_x, knuckle_inclination)
        force = mz_0 / knuckle_x / np.sin(knuckle_inclination)
        dn_0 = force * np.cos(knuckle_inclination)
        knuckle.hangers[0].prestressing_force = -force
        knuckle.hangers[0].cross_section = cs_knuckle
        knuckles = Hangers(nodes, knuckle, span)
        tie.assign_hangers(knuckles)
        arch.arch_connection_nodes(nodes, knuckles)
        self.hanger_sets.extend(knuckles.hanger_sets)
        return knuckles, dn_0

    def plot_elements(self, ax):
        for hanger in self:
            x = [hanger.tie_node.x, hanger.arch_node.x]
            y = [hanger.tie_node.y, hanger.arch_node.y]
            ax.plot(x, y, color='black', linewidth=0.7)
        return

    def plot_effects(self, ax, name, label='', c='black', lw=1.0, ls='-'):
        n = len(self.hanger_sets[0])
        effects = self.get_range(name)['Normal Force']
        if effects.ndim == 1:
            values = effects[0:n]
        else:
            values = effects[:, 0:n]
        tie_node_x = [hanger.tie_node.x for hanger in self.hanger_sets[0]]
        resistances = np.array([hanger.cross_section.normal_force_resistance for hanger in self.hanger_sets[0]])

        if effects.ndim == 1:
            ax.plot(tie_node_x, values/resistances, label=label, c=c, lw=lw, ls=ls)
        else:
            ax.plot(tie_node_x, values[0, :]/resistances, label=label, c=c, lw=lw, ls=ls)
            ax.plot(tie_node_x, values[1, :]/resistances, c=c, lw=lw, ls=ls)
        return
