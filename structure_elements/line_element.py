import numpy as np

from plotting.model import plot_model
from plotting.save import save_plot
from structure_analysis import structure_analysis
from structure_elements.effects import multiply_effect
from structure_elements.element import Element


class LineElement(Element):
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.cross_sections = []
        self.regions = []
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
                    if self.cross_sections:
                        self.cross_sections.insert(i, self.cross_sections[i])
                    break
        return node

    def segment_length(self, i):
        dx = self.nodes[i+1].x - self.nodes[i].x
        dy = self.nodes[i+1].y - self.nodes[i].y
        length = (dx ** 2 + dy ** 2)**0.5
        return length

    def define_cross_sections(self, nodes, section_nodes, cross_sections):
        if section_nodes and type(section_nodes) is list:
            section_nodes = [self.insert_node(nodes, x) for x in section_nodes]
        self.cross_sections = []
        section_nodes += [self.nodes[-1]]

        for cross_section in cross_sections:
            cross_section.length = 0

        j = 0
        for i in range(len(self.nodes) - 1):
            length = self.segment_length(i)
            if self.nodes[i] == section_nodes[j]:
                j += 1
            self.cross_sections.append(cross_sections[j])
            cross_sections[j].length += length
        return

    def get_beams(self):
        n = len(self)
        beams_nodes = [[self.nodes[i].index, self.nodes[i + 1].index] for i in range(n)]
        beams_stiffness = []
        for i in range(n):
            beams_stiffness.append(self.cross_sections[i].get_beam())
        return beams_nodes, beams_stiffness

    def self_weight(self, first_index=0):
        load_distributed = []
        for i, cross_section in enumerate(self.cross_sections):
            load_distributed.append(cross_section.get_self_weight(i + first_index))
        load_group = {'Distributed': load_distributed}
        return load_group

    def load_group_utilities(self):
        return {}

    def permanent_loads(self):
        load_group = self.self_weight()
        load_group_dw = self.load_group_utilities()
        if load_group_dw:
            load_group['Nodal'].extend(load_group_dw['Nodal'])
        return load_group

    def distributed_load(self, q, x_start, x_end, first_index=0):
        load_distributed = []
        for i in range(len(self.nodes) - 1):
            x_1 = self.nodes[i].x
            x_2 = self.nodes[i + 1].x
            if x_2 > x_start:
                load_distributed.append([i + first_index, max(0, x_start - x_1), 0, 0, -q, 0, 0, -q, 0])
            if x_2 >= x_end:
                load_distributed[-1][2] = x_end - x_2
                break
        load_group = {'Distributed': load_distributed}
        return load_group

    def concentrated_load(self, x, force, first_index=0):
        load_group = {}
        for i in range(len(self.nodes) - 1):
            x_start = self.nodes[i].x
            x_end = self.nodes[i + 1].x
            if x_start <= x < x_end:
                load_group = {'Point': [[i + first_index, x - x_start, 0, force, 0]]}
                break
        return load_group

    def assign_range_to_sections(self, name):
        effects = self.get_effects(name)
        cs_i = self.get_cross_sections()
        for cs in set(self.cross_sections):
            mask = cs_i == cs
            for key in effects:
                if effects[key].ndim == 1:
                    cs.assign_extrema(effects[key][mask], name, key)
                else:
                    cs.assign_extrema(effects[key][:, mask], name, key)
            cs.calculate_doc_max(name)
        return

    def get_coordinates(self):
        xy_coord = np.empty((0, 2))
        for i in range(len(self.nodes) - 1):
            x_start, x_end = self.nodes[i].x, self.nodes[i + 1].x
            y_start, y_end = self.nodes[i].y, self.nodes[i + 1].y
            length = ((x_start - x_end) ** 2 + (y_start - y_end) ** 2) ** 0.5
            x = np.linspace(x_start, x_end, num=int(np.ceil(length)) + 1)
            y = np.linspace(y_start, y_end, num=int(np.ceil(length)) + 1)
            xy_coord = np.vstack((xy_coord, np.vstack((x, y)).transpose()))
        return xy_coord

    def get_cross_sections(self):
        cs_i = []
        for i in range(len(self.nodes) - 1):
            x_start, x_end = self.nodes[i].x, self.nodes[i + 1].x
            y_start, y_end = self.nodes[i].y, self.nodes[i + 1].y
            length = ((x_start - x_end) ** 2 + (y_start - y_end) ** 2) ** 0.5
            cs_i.extend([self.cross_sections[i] for j in range(int(np.ceil(length)) + 1)])
        cs_i = np.array(cs_i)
        return cs_i

    def calculate_doc(self, name):
        cs_i = self.get_cross_sections()
        dc_1 = np.zeros_like(self.effects[name]['Normal Force'])
        dc_2 = np.zeros_like(self.effects[name]['Normal Force'])
        if 'Normal Force' in self.effects[name]:
            resistances_n = np.array([cs.normal_force_resistance for cs in cs_i])
            dc_1 += self.effects[name]['Normal Force'] / resistances_n
            dc_2 += self.effects[name]['Normal Force'] / resistances_n
        if 'Moment' in self.effects[name]:
            resistances_mz = np.array([cs.moment_z_resistance for cs in cs_i])
            dc_1 += 8/9 * self.effects[name]['Moment'] / resistances_mz
            dc_2 -= 8/9 * self.effects[name]['Moment'] / resistances_mz
        self.set_effects(dc_1, name, 'D/C_1')
        self.set_effects(dc_2, name, 'D/C_2')
        return

    def set_effects(self, effects, name, key=None):
        super().set_effects(effects, name, key=key)
        if not key and 'D/C_1' not in effects:
            self.calculate_doc(name)
        return

    def plot_elements(self, ax):
        for i in range(len(self.nodes) - 1):
            x = [self.nodes[i].x, self.nodes[i + 1].x]
            y = [self.nodes[i].y, self.nodes[i + 1].y]
            ax.plot(x, y, color='black', linewidth=1.5)
        return

    def plot_effects(self, ax, name, key, label='', c='black', lw=1.0, ls='-'):
        effects = self.get_range(name)[key]
        xy_coord = self.get_coordinates()
        if effects.ndim == 1:
            ax.plot(xy_coord[:, 0], effects / 1000, label=label, c=c, lw=lw, ls=ls)
        else:
            ax.plot(xy_coord[:, 0], effects[0, :] / 1000, label=label, c=c, lw=lw, ls=ls)
            ax.plot(xy_coord[:, 0], effects[1, :] / 1000, c=c, lw=lw, ls=ls)
        return

    # def plot_effects_on_arch(self, ax, nodes, name, key, reaction_amax=0, show_extrema=False, color_line='red', color_fill='orange'):
    #
    #     max_color = 'red'  # Color used for max values
    #     min_color = 'blue'  # Color used for min values
    #
    #     if type(name) is str:
    #         if name in self.effects_range:
    #             plot_range = True
    #             reactions = self.effects_range[name]['Max'][key]
    #             reactions_2 = self.effects_range[name]['Min'][key]
    #         else:
    #             plot_range = False
    #             reactions = self.get_effects(name, key=key)
    #             reactions_2 = self.get_effects(name, key=key)
    #     else:
    #         plot_range = False
    #         reactions = name[key]
    #         reactions_2 = name[key]
    #
    #     scale = get_scaling(nodes, reactions, reactions_2, reaction_abs_max=reaction_amax)
    #
    #     values_1 = get_value_list(reactions)
    #     values_2 = get_value_list(reactions_2)
    #     values_3 = get_value_list_2(reactions, reactions_2)
    #
    #     xy_coord = get_coordinates(self, reactions)
    #     normal_vec = get_normal_vectors(self, reactions)
    #
    #     xy_values_1 = get_value_location(xy_coord, normal_vec, values_1, scale)
    #     xy_values_2 = get_value_location(xy_coord, normal_vec, values_2, scale)
    #     xy_values_3 = get_value_location(xy_coord, normal_vec, values_3, scale)
    #
    #     # Plot the impacts
    #     ax.plot(xy_values_1[:, 0], xy_values_1[:, 1], color=color_line, alpha=0.4)
    #     if not plot_range:
    #         xy = np.vstack((xy_values_1, xy_coord[::-1,:]))
    #         polygon = Polygon(xy, edgecolor=None, fill=True, facecolor=color_fill, alpha=0.3)
    #         ax.add_patch(polygon)
    #     else:
    #         ax.plot(xy_values_2[:, 0], xy_values_2[:, 1], color=color_line, alpha=0.4)
    #
    #         xy = np.vstack((xy_values_1, xy_values_2[::-1, :]))
    #         polygon = Polygon(xy, edgecolor=None, fill=True, facecolor=color_fill, alpha=0.5)
    #         ax.add_patch(polygon)
    #
    #         xy = np.vstack((xy_values_3, xy_coord[::-1, :]))
    #         polygon = Polygon(xy, edgecolor=None, fill=True, facecolor=color_fill, alpha=0.3)
    #         ax.add_patch(polygon)
    #
    #     # if show_extrema:
    #     #     for i in range(len(self.sections_set)):
    #     #         ax.plot(0, 0, linestyle='None', label=self.sections_set[i])
    #     #
    #     #         ax.plot(x_max[i], y_max[i], color=max_color, marker='.', markersize=10, linestyle='None',
    #     #                 label=f'max: {r_max[i]/1000:.0f} MNm')
    #     #         ax.plot(x_min[i], y_min[i], color=min_color, marker='.', markersize=10, linestyle='None',
    #     #                 label=f'min: {r_min[i]/1000:.0f} MNm')
    #     #     ax.legend(frameon=False, loc='center left', bbox_to_anchor=(1, 0.5))
    #     return

    def assign_permanent_effects(self, nodes, hangers, f_x, m_z, plots=False, name='Line Element', weight=True):
        # Define the list of all nodes
        structural_nodes = nodes.structural_nodes()
        beams_nodes, beams_stiffness = self.get_beams()
        beams = {'Nodes': beams_nodes, 'Stiffness': beams_stiffness}
        load_group = self.permanent_loads()

        load_nodal = [[self.nodes[0].index, f_x, 0, -m_z], [self.nodes[-1].index, -f_x, 0, m_z]]

        # Apply hanger forces
        for hanger in hangers:
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
        if 'Nodal' in load_group:
            load_group['Nodal'].extend(load_nodal)
        else:
            load_group['Nodal'] = load_nodal
        loads = [load_group]
        restricted_degrees = [[self.nodes[0].index, 1, 1, 0, 0], [self.nodes[-1].index, 0, 1, 0, 0]]
        boundary_conditions = {'Restricted Degrees': restricted_degrees}
        model = {'Nodes': structural_nodes, 'Beams': beams, 'Loads': loads,
                 'Boundary Conditions': boundary_conditions}
        d, i_f, rd, sp = structure_analysis(model, discType='Lengthwise', discLength=1)

        self.set_effects(i_f[0], 'Permanent')
        effects = self.get_effects('Permanent')
        self.set_effects(multiply_effect(effects, 0), '0')

        # Create the plots if needed
        if plots:
            fig, ax = plot_model(model, self)
            save_plot(fig, 'Models', name)

            fig, ax = plot_model(model, self, i=None, show=False)
            # self.plot_effects_on_arch(ax, nodes, 'Permanent', 'Moment')
            save_plot(fig, 'Effects', name)
        return
