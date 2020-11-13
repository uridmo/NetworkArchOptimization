import numpy as np
from math import inf
from matplotlib.patches import Polygon

from structure_analysis import structure_analysis
from structure_analysis.plotting import plot_loads, plot_internal_forces
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
            x = self.nodes[-1].x - x if x < 0 else x
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
        return

    def beams(self):
        n = len(self)
        beams_nodes = [[self.nodes[i].index, self.nodes[i + 1].index] for i in range(n)]
        beams_stiffness = n * [[self.axial_stiffness, self.bending_stiffness]]
        return beams_nodes, beams_stiffness

    def self_weight(self, indices=range(0)):
        if not indices:
            indices = range(len(self))
        q = self.weight
        load_distributed = [[i, 0, 0, 0, -q, 0, 0, -q, 0] for i in indices]
        return load_distributed

    def calculate_permanent_impacts(self, nodes, hangers, f_x, m_z, plots=False):
        # Define the list of all nodes
        structural_nodes = nodes.structural_nodes()
        beams_nodes, beams_stiffness = self.beams()
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
            plot_loads(model, 0, 'Tie permanent impacts')
            plot_internal_forces(model, d, i_f, 0, 'Moment', 'Tie permanent impacts')
        return

    def assign_range_to_sections(self):
        for key in self.effects_range:
            effects_max = self.effects_range[key]['Max']
            effects_min = self.effects_range[key]['Min']
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

    def plot_effects(self, ax, nodes, name, key, reaction_amax=0, color_line='red', color_fill='orange'):
        nodes_location = nodes.structural_nodes()['Location']
        elements, k = self.beams()

        x_min = min([node.x for node in nodes])
        x_max = max([node.x for node in nodes])
        z_min = min([node.y for node in nodes])
        z_max = max([node.y for node in nodes])
        diag_length = (((x_max - x_min) ** 2 + (z_max - z_min) ** 2) ** 0.5)

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
            if name is dict:
                plot_range = True
                reactions = name['Max'][key]
                reactions_2 = name['Min'][key]
            else:
                plot_range = False
                reactions = name[key]
                reactions_2 = name[key]

        if not reaction_amax:
            reaction_max = max([max(sublist) for sublist in reactions])
            reaction_min = min([min(sublist) for sublist in reactions])
            reaction_amax = max(reaction_max, -reaction_min)

        # Define scaling
        if reaction_amax > 1e-6:
            scale = diag_length / 12 / reaction_amax
        else:
            scale = 0

        x_arch = np.array([])
        y_arch = np.array([])
        x_react = np.array([])
        y_react = np.array([])
        x_react_2 = np.array([])
        y_react_2 = np.array([])
        x_react_3 = np.array([])
        y_react_3 = np.array([])

        # Cycle through elements
        for i, reaction in enumerate(reactions):
            start, end = elements[i][0], elements[i][1]
            x = np.linspace(nodes_location[start][0], nodes_location[end][0], num=len(reaction))
            y = np.linspace(nodes_location[start][1], nodes_location[end][1], num=len(reaction))

            # Construct unit vector perpendicular to the corresponding element accoring to
            # sign convention
            dx = (nodes_location[end][0] - nodes_location[start][0])
            dy = (nodes_location[end][1] - nodes_location[start][1])
            dl = (dx ** 2 + dy ** 2) ** 0.5
            normal_vec = [dy / dl, -dx / dl]

            # Absolute coordinates for displaying the values
            values = np.array(reaction)
            x_impact = x + normal_vec[0] * scale * values
            y_impact = y + normal_vec[1] * scale * values

            # Append the arrays
            x_arch = np.append(x_arch, x)
            y_arch = np.append(y_arch, y)
            x_react = np.append(x_react, x_impact)
            y_react = np.append(y_react, y_impact)

            if plot_range:
                values_2 = np.array(reactions_2[i])
                x_impact_2 = x + normal_vec[0] * scale * values_2
                y_impact_2 = y + normal_vec[1] * scale * values_2
                x_react_2 = np.append(x_react_2, x_impact_2)
                y_react_2 = np.append(y_react_2, y_impact_2)
                values_3 = np.array([np.max((np.min((0, values_2[i])), values[i])) for i in range(len(values_2))])
                x_impact_3 = x + normal_vec[0] * scale * values_3
                y_impact_3 = y + normal_vec[1] * scale * values_3
                x_react_3 = np.append(x_react_3, x_impact_3)
                y_react_3 = np.append(y_react_3, y_impact_3)

        # Plot the impacts
        ax.plot(x_react, y_react, color=color_line, alpha=0.4)
        if plot_range:
            ax.plot(x_react_2, y_react_2, color=color_line, alpha=0.4)

        # Fill it with a polygon
        if not plot_range:
            x_fill = np.concatenate((x_react, x_arch[::-1]))
            y_fill = np.concatenate((y_react, y_arch[::-1]))
        else:
            x_fill = np.concatenate((x_react_3, x_arch[::-1]))
            y_fill = np.concatenate((y_react_3, y_arch[::-1]))
            xy_poly = np.stack((x_fill, y_fill))
            polygon = Polygon(np.transpose(xy_poly), edgecolor=None, fill=True, facecolor=color_fill, alpha=0.3)
            ax.add_patch(polygon)

            x_fill = np.concatenate((x_react, x_react_2[::-1]))
            y_fill = np.concatenate((y_react, y_react_2[::-1]))
        xy_poly = np.stack((x_fill, y_fill))
        polygon = Polygon(np.transpose(xy_poly), edgecolor=None, fill=True, facecolor=color_fill, alpha=0.5)
        ax.add_patch(polygon)
        return

