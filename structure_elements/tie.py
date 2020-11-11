import numpy as np

from structure_analysis import structure_analysis
from structure_analysis.plotting import plot_loads
from structure_analysis.plotting import plot_internal_forces
from structure_elements.line_element import LineElement


class Tie(LineElement):
    def __init__(self, nodes, span, g, ea, ei, ga=0):
        super().__init__(g, ea, ei, ga=ga)
        self.start_node = nodes.add_node(0, 0)
        self.end_node = nodes.add_node(span, 0)
        self.nodes = [self.start_node] + [self.end_node]
        self.hangers = [[], []]
        self.permanent_impacts = None

    def __len__(self):
        return len(self.nodes)-1

    def assign_hangers(self, hangers):
        hangers.hangers.sort(key=lambda n: n.tie_node.x)
        for hanger in hangers.hangers:
            if hanger.tie_node not in self.nodes:
                for i in range(len(self.nodes)-1):
                    if self.nodes[i+1].x > hanger.tie_node.x:
                        break
                self.nodes.insert(i+1, hanger.tie_node)
                self.hangers.insert(i+1, [hanger])
            else:
                i = self.nodes.index(hanger.tie_node)
                self.hangers[i].append(hanger)
        return

    def insert_node(self, nodes, x, y):
        node = nodes.add_node(x, y)
        if node not in self.nodes:
            for i in range(len(self.nodes)-1):
                if self.nodes[i].x < x < self.nodes[i+1].x:
                    self.nodes.insert(i+1, node)
                    self.hangers.insert(i+1, [])
                    break
        return

    # def calculate_permanent_impacts(self, nodes, f_x, m_z, plots=False):
    #     # Define the list of all nodes
    #     structural_nodes = nodes.structural_nodes()
    #
    #     # Define the structural beams
    #     beams_nodes, beams_stiffness = self.get_beams()
    #     beams = {'Nodes': beams_nodes, 'Stiffness': beams_stiffness}
    #
    #     # Apply self weight
    #     load_distributed = self.self_weight_loads()
    #
    #     # Apply global self-stresses
    #     load_nodal = [[self.nodes[0].index, f_x, 0, -m_z], [self.nodes[-1].index, -f_x, 0, m_z]]
    #
    #     # Apply hanger forces
    #     for hanger_group in self.hangers:
    #         for hanger in hanger_group:
    #             if hanger.tie_node in self.nodes:
    #                 node = hanger.tie_node.index
    #                 vertical_force = hanger.prestressing_force * np.sin(hanger.inclination)
    #                 horizontal_force = hanger.prestressing_force * np.cos(hanger.inclination)
    #                 load_nodal.append([node, horizontal_force, vertical_force, 0])
    #             if hanger.arch_node in self.nodes:
    #                 node = hanger.arch_node.index
    #                 vertical_force = -hanger.prestressing_force * np.sin(hanger.inclination)
    #                 horizontal_force = -hanger.prestressing_force * np.cos(hanger.inclination)
    #                 load_nodal.append([node, horizontal_force, vertical_force, 0])
    #
    #     # Assign the load group
    #     load_group = {'Distributed': load_distributed, 'Nodal': load_nodal}
    #     loads = [load_group]
    #
    #     # Define the boundary conditions
    #     restricted_degrees = [[self.nodes[0].index, 1, 1, 0, 0], [self.nodes[-1].index, 0, 1, 0, 0]]
    #     boundary_conditions = {'Restricted Degrees': restricted_degrees}
    #
    #     # Calculate and assign the permanent impacts
    #     model = {'Nodes': structural_nodes, 'Beams': beams, 'Loads': loads,
    #              'Boundary Conditions': boundary_conditions}
    #     d_tie, if_tie, rd_tie = structure_analysis(model, discType='Lengthwise', discLength=1)
    #     self.impacts['Permanent'] = if_tie[0]
    #
    #     # Create the plots if needed
    #     if plots:
    #         plot_loads(model, 0, 'Tie permanent impacts')
    #         plot_internal_forces(model, d_tie, if_tie, 0, 'Normal Force', 'Tie permanent impacts')
    #     return
