import numpy as np

from structure_analysis import structure_analysis
from structure_elements.line_element import LineElement


class Tie(LineElement):
    def __init__(self, nodes, span, n, g_deck, g_wearing):
        super().__init__()
        self.span = span
        self.cross_girders_amount = n
        self.cross_girders_nodes = [nodes.add_node(span*(i+1)/(n+1), 0) for i in range(n)]
        self.nodes = [nodes.add_node(0, 0)] + self.cross_girders_nodes + [nodes.add_node(span, 0)]
        self.weight_deck = g_deck
        self.weight_utilities = g_wearing

        self.force_deck = self.weight_deck * self.span / (self.cross_girders_amount + 1)
        self.force_utilities = self.weight_utilities * self.span / (self.cross_girders_amount + 1)

    def assign_hangers(self, hangers):
        for hanger in hangers:
            if hanger.tie_node not in self.nodes:
                for i in range(len(self.nodes)-1):
                    if self.nodes[i+1].x > hanger.tie_node.x:
                        self.nodes.insert(i+1, hanger.tie_node)
                        if self.cross_sections:
                            self.cross_sections.insert(i, self.cross_sections[i])
                        break
            else:
                i = self.nodes.index(hanger.tie_node)
        return

    def self_weight(self, first_index=0):
        load_group = super(Tie, self).self_weight(first_index=first_index)
        f_y = -self.weight_deck * self.span / (self.cross_girders_amount+1)
        load_group['Nodal'] = [[node.index, 0, f_y, 0] for node in self.cross_girders_nodes[1:-1]]
        load_group['Nodal'].append([self.cross_girders_nodes[0].index, 0, 1.0*f_y, 0])
        load_group['Nodal'].append([self.cross_girders_nodes[-1].index, 0, 1.0*f_y, 0])
        load_group['Nodal'].append([self.nodes[0].index, 0, 0.5*f_y, 0])
        load_group['Nodal'].append([self.nodes[-1].index, 0, 0.5*f_y, 0])
        return load_group

    def load_group_utilities(self):
        load_group = {}
        f_y = -self.weight_utilities * self.span / (self.cross_girders_amount + 1)
        load_group['Nodal'] = [[node.index, 0, f_y, 0] for node in self.cross_girders_nodes[1:-1]]
        load_group['Nodal'].append([self.cross_girders_nodes[0].index, 0, 1.0*f_y, 0])
        load_group['Nodal'].append([self.cross_girders_nodes[-1].index, 0, 1.0*f_y, 0])
        return load_group

    def weight(self):
        weight = self.weight_deck * self.span
        for i, cross_section in enumerate(self.cross_sections):
            dx = self.nodes[i+1].x - self.nodes[i].x
            g = cross_section.weight
            weight += dx * g
        return weight

    def zero_displacement(self, nodes, hangers, dof_rz=True, plot=False):
        structural_nodes = nodes.structural_nodes()
        beams_nodes, beams_stiffness = self.get_beams()
        beams = {'Nodes': beams_nodes, 'Stiffness': beams_stiffness}
        load_group = self.permanent_loads()

        restricted_degrees = [[self.nodes[0].index, 1, 1, int(dof_rz), 0]]
        restricted_degrees += [[self.nodes[-1].index, 1, 1, int(dof_rz), 0]]
        x_coord, nodes = hangers.get_connection_points()
        for node in nodes:
            restricted_degrees += [[node.index, 0, 1, 0, 0]]

        boundary_conditions = {'Restricted Degrees': restricted_degrees}
        model = {'Nodes': structural_nodes, 'Beams': beams, 'Loads': [load_group],
                 'Boundary Conditions': boundary_conditions}

        d_tie, if_tie, rd_tie, sp_tie = structure_analysis(model)
        mz_0 = if_tie[0]['Moment'][0][0] if dof_rz else 0

        # Assign the reaction forces to the hangers
        forces = [rd[2] for rd in rd_tie[0][2:]]
        hangers.set_prestressing_force_from_nodes(nodes, forces)
        return mz_0

    def calculate_fracture_stress(self, effect_name):
        cs_i = self.get_cross_sections()
        effects = self.get_effects(effect_name)
        for cs in set(cs_i):
            mask = cs == cs_i
            for tie_fracture in cs.tie_fractures:
                name = tie_fracture.name
                if name+'_top' not in effects:
                    effects[name+'_top'] = np.zeros_like(effects['Normal Force'])
                    effects[name+'_bot'] = np.zeros_like(effects['Normal Force'])
                o_top, o_bot = tie_fracture.calculate_stress(effects, mask)
                effects[name+'_top'][mask] = o_top
                effects[name+'_bot'][mask] = o_bot
        return
