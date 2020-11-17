from math import inf

import numpy as np
from matplotlib.patches import Polygon

from plotting.line import get_scaling, get_value_list, get_value_list_2, get_value_location, \
    get_coordinates, get_normal_vectors
from plotting.model import plot_model
from plotting.save import save_plot
from structure_analysis import structure_analysis
from structure_elements.effects import multiply_effect
from structure_elements.element import Element


class LineElement(Element):
    def __init__(self, g, ea, ei, ga=0):
        super().__init__()
        self.nodes = []
        self.sections = []
        self.sections_set = []
        self.weight = g
        self.axial_stiffness = ea
        self.bending_stiffness = ei
        self.shear_stiffness = ga
        self.effects_section = {}

        return

    def __len__(self):
        return len(self.nodes) - 1

    def insert_node(self, nodes, x, y=None):
        if y is None:
            x_ref = [node.x for node in self.nodes]
            y_ref = [node.y for node in self.nodes]
            x = self.nodes[-1].x + x if x < 0 else x
            y = np.interp(x, x_ref, y_ref)
        node = nodes.add_node(x, y)
        if node not in self.nodes:
            for i in range(len(self.nodes) - 1):
                if self.nodes[i].x < x < self.nodes[i + 1].x:
                    self.nodes.insert(i + 1, node)
                    break
        return node

    def define_region(self, nodes, section_nodes, names):
        if section_nodes and type(section_nodes) is list:
            section_nodes = [self.insert_node(nodes, x) for x in section_nodes]
        self.sections = []
        section_nodes += [self.nodes[-1]]
        j = 0
        for i in range(len(self.nodes)-1):

            if self.nodes[i] == section_nodes[j]:
                j += 1
            self.sections.append(names[j])
        self.sections_set = list(set(self.sections))
        self.sections_set.sort()
        return

    def get_beams(self):
        n = len(self)
        beams_nodes = [[self.nodes[i].index, self.nodes[i + 1].index] for i in range(n)]
        beams_stiffness = n * [[self.axial_stiffness, self.bending_stiffness]]
        return beams_nodes, beams_stiffness

    def self_weight(self, indices=range(0)):
        if not indices:
            indices = range(len(self))
        g = self.weight
        load_distributed = [[i, 0, 0, 0, -g, 0, 0, -g, 0] for i in indices]
        return load_distributed

    def distributed_load(self, q, x_start, x_end, first_index=0):
        load_distributed = []
        for i in range(len(self.nodes)-1):
            x_1 = self.nodes[i].x
            x_2 = self.nodes[i+1].x
            if x_2 > x_start:
                load_distributed.append([i+first_index, max(0, x_start-x_1), 0, 0, -q, 0, 0, -q, 0])
            if x_2 >= x_end:
                load_distributed[-1][2] = x_end-x_2
                break
        loads = {'Distributed': load_distributed}
        return loads

    def concentrated_live_load(self, x_ref, first_index=0):
        x_1 = x_ref - 4.3
        x_2 = x_ref
        x_3 = x_ref + 4.3
        load_point = []
        for i in range(len(self.nodes)-1):
            x_start = self.nodes[i].x
            x_end = self.nodes[i+1].x
            if x_start <= x_1 < x_end:
                load_point.append([i+first_index, x_1 - x_start, 0, -145, 0])
            if x_start <= x_2 < x_end:
                load_point.append([i+first_index, x_2 - x_start, 0, -145, 0])
            if x_start <= x_3 < x_end:
                load_point.append([i+first_index, x_3 - x_start, 0, -35, 0])
                break
        loads = {'Point': load_point}
        return loads

    def calculate_permanent_impacts(self, nodes, hangers, f_x, m_z, plots=False, name='Line Element'):
        # Define the list of all nodes
        structural_nodes = nodes.structural_nodes()
        beams_nodes, beams_stiffness = self.get_beams()
        beams = {'Nodes': beams_nodes, 'Stiffness': beams_stiffness}
        load_distributed = self.self_weight()
        load_nodal = [[self.nodes[0].index, f_x, 0, -m_z], [self.nodes[-1].index, -f_x, 0, m_z]]

        # Apply hanger forces
        for hanger in hangers.hangers:
            if hanger.tie_node in self.nodes:
                node = hanger.tie_node.index
                vertical_force = hanger.prestressing_force * np.sin(hanger.inclination)
                horizontal_force = hanger.prestressing_force * np.cos(hanger.inclination)
                load_nodal.append([node, horizontal_force, vertical_force, 0])
            if hanger.arch_node in self.nodes:
                node = hanger.arch_node.index
                vertical_force = -hanger.prestressing_force * np.sin(hanger.inclination)
                horizontal_force = -hanger.prestressing_force * np.cos(hanger.inclination)
                load_nodal.append([node, horizontal_force, vertical_force, 0])

        # Assign the load group
        load_group = {'Distributed': load_distributed, 'Nodal': load_nodal}
        loads = [load_group]
        restricted_degrees = [[self.nodes[0].index, 1, 1, 0, 0], [self.nodes[-1].index, 0, 1, 0, 0]]
        boundary_conditions = {'Restricted Degrees': restricted_degrees}
        model = {'Nodes': structural_nodes, 'Beams': beams, 'Loads': loads,
                 'Boundary Conditions': boundary_conditions}
        d, i_f, rd = structure_analysis(model, discType='Lengthwise', discLength=1)

        self.effects['Permanent'] = i_f[0]
        self.set_effects(i_f[0], 'Permanent')
        self.set_effects(multiply_effect(i_f[0], 0), '0')

        # Create the plots if needed
        if plots:
            fig, ax = plot_model(model, self)
            save_plot(fig, 'Models', name)

            fig, ax = plot_model(model, self, i=None, show=False)
            self.plot_effects_on_arch(ax, nodes, 'Permanent', 'Moment')
            save_plot(fig, 'Effects', name)
        return

    def assign_range_to_sections(self):
        for key in self.effects:
            effects = self.effects[key]
            if 'Max' in effects:
                effects_max = effects['Max']
                effects_min = effects['Min']
            else:
                effects_max = effects
                effects_min = effects
            self.effects_section[key] = {}
            for eff in effects_min:
                max_0 = [-inf for i in self.sections_set]
                min_0 = [inf for i in self.sections_set]
                self.effects_section[key][eff] = {'Max': max_0, 'Min': min_0}
                for i in range(len(effects_max[eff])):
                    section = self.sections[i]
                    section_i = self.sections_set.index(section)
                    max_new = max(self.effects_section[key][eff]['Max'][section_i], max(effects_max[eff][i]))
                    min_new = min(self.effects_section[key][eff]['Min'][section_i], min(effects_max[eff][i]))
                    self.effects_section[key][eff]['Max'][section_i] = max_new
                    self.effects_section[key][eff]['Min'][section_i] = min_new
        return

    def plot_elements(self, ax):
        for i in range(len(self.nodes)-1):
            x = [self.nodes[i].x, self.nodes[i+1].x]
            y = [self.nodes[i].y, self.nodes[i+1].y]
            ax.plot(x, y, color='black', linewidth=1.5)
        return

    def plot_effects(self, ax, name, key, extrema='', color='black', ls='-'):

        if extrema:
            effects = self.effects[name][extrema][key]
        else:
            if 'Min' in self.get_effects(name):
                self.plot_effects(ax, name, key, extrema='Min', color=color, ls='--')
                effects = self.get_effects(name)['Max'][key]
            else:
                effects = self.get_effects(name)[key]

        xy_coord = get_coordinates(self, effects)
        values = get_value_list(effects)/1000
        ax.plot(xy_coord[:, 0], values, color=color, ls=ls)
        return

    def plot_range(self, ax, name, key, color='black'):

        self.plot_effects(ax, name, key, extrema='Max', color=color)
        self.plot_effects(ax, name, key, extrema='Min', color=color)

        return

    def plot_effects_on_arch(self, ax, nodes, name, key, reaction_amax=0, show_extrema=False, color_line='red', color_fill='orange'):

        max_color = 'red'  # Color used for max values
        min_color = 'blue'  # Color used for min values

        if type(name) is str:
            if name in self.effects_range:
                plot_range = True
                reactions = self.effects_range[name]['Max'][key]
                reactions_2 = self.effects_range[name]['Min'][key]
            else:
                plot_range = False
                reactions = self.get_effects(name, key=key)
                reactions_2 = self.get_effects(name, key=key)
        else:
            plot_range = False
            reactions = name[key]
            reactions_2 = name[key]

        scale = get_scaling(nodes, reactions, reactions_2, reaction_abs_max=reaction_amax)

        values_1 = get_value_list(reactions)
        values_2 = get_value_list(reactions_2)
        values_3 = get_value_list_2(reactions, reactions_2)

        xy_coord = get_coordinates(self, reactions)
        normal_vec = get_normal_vectors(self, reactions)

        xy_values_1 = get_value_location(xy_coord, normal_vec, values_1, scale)
        xy_values_2 = get_value_location(xy_coord, normal_vec, values_2, scale)
        xy_values_3 = get_value_location(xy_coord, normal_vec, values_3, scale)

        # Plot the impacts
        ax.plot(xy_values_1[:, 0], xy_values_1[:, 1], color=color_line, alpha=0.4)
        if not plot_range:
            xy = np.vstack((xy_values_1, xy_coord[::-1,:]))
            polygon = Polygon(xy, edgecolor=None, fill=True, facecolor=color_fill, alpha=0.3)
            ax.add_patch(polygon)
        else:
            ax.plot(xy_values_2[:, 0], xy_values_2[:, 1], color=color_line, alpha=0.4)

            xy = np.vstack((xy_values_1, xy_values_2[::-1, :]))
            polygon = Polygon(xy, edgecolor=None, fill=True, facecolor=color_fill, alpha=0.5)
            ax.add_patch(polygon)

            xy = np.vstack((xy_values_3, xy_coord[::-1, :]))
            polygon = Polygon(xy, edgecolor=None, fill=True, facecolor=color_fill, alpha=0.3)
            ax.add_patch(polygon)

        # if show_extrema:
        #     for i in range(len(self.sections_set)):
        #         ax.plot(0, 0, linestyle='None', label=self.sections_set[i])
        #
        #         ax.plot(x_max[i], y_max[i], color=max_color, marker='.', markersize=10, linestyle='None',
        #                 label=f'max: {r_max[i]/1000:.0f} MNm')
        #         ax.plot(x_min[i], y_min[i], color=min_color, marker='.', markersize=10, linestyle='None',
        #                 label=f'min: {r_min[i]/1000:.0f} MNm')
        #     ax.legend(frameon=False, loc='center left', bbox_to_anchor=(1, 0.5))
        return

