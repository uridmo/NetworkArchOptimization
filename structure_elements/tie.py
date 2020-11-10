import numpy as np

from structure_analysis import structure_analysis
from structure_analysis.plotting import plot_loads
from structure_analysis.plotting import plot_internal_forces


class Tie:
    def __init__(self, nodes, span, hangers, g, ea, ei, ga=0):
        self.span = span
        self.start_node = nodes.add_node(0, 0)
        self.end_node = nodes.add_node(span, 0)

        hangers.hangers.sort(key=lambda n: n.tie_node.x)

        self.middle_nodes = []
        self.hanger_group = []
        for hanger in hangers.hangers:
            if hanger.tie_node not in self.middle_nodes:
                self.middle_nodes += [hanger.tie_node]
                self.hanger_group += [[hanger]]
            else:
                i = self.middle_nodes.index(hanger.tie_node)
                self.hanger_group[i].append(hanger)

        self.nodes = [self.start_node] + self.middle_nodes + [self.end_node]

        self.weight = g
        self.axial_stiffness = ea
        self.bending_stiffness = ei
        self.shear_stiffness = ga
        self.permanent_impacts = None

    def __len__(self):
        return len(self.nodes)-1

    def get_beams(self):
        n = len(self)
        beams_nodes = [[self.nodes[i].index, self.nodes[i + 1].index] for i in range(n)]
        beams_stiffness = n * [[self.axial_stiffness, self.bending_stiffness]]
        return beams_nodes, beams_stiffness

    def self_weight_loads(self, indices=range(0)):
        if not indices:
            indices = range(len(self))
        q = self.weight
        load_distributed = [[i, 0, 0, 0, -q, 0, 0, -q, 0] for i in indices]
        return load_distributed

    def calculate_permanent_impacts(self, nodes, n_0, mz_0, plots=False):
        # Define the list of all nodes
        structural_nodes = nodes.structural_nodes()

        # Define the structural beams
        beams_nodes, beams_stiffness = self.get_beams()
        beams = {'Nodes': beams_nodes, 'Stiffness': beams_stiffness}

        # Apply self weight
        load_distributed = self.self_weight_loads()

        # Apply global self-stresses
        load_nodal = [[self.nodes[0].index, n_0, 0, -mz_0], [self.nodes[-1].index, -n_0, 0, mz_0]]

        # Apply hanger forces
        for hanger_group in self.hanger_group:
            for hanger in hanger_group:
                node = hanger.tie_node.index
                vertical_force = hanger.prestressing_force * np.sin(hanger.inclination)
                horizontal_force = hanger.prestressing_force * np.cos(hanger.inclination)
                load_nodal.append([node, horizontal_force, vertical_force, 0])

        # Assign the load group
        load_group = {'Distributed': load_distributed, 'Nodal': load_nodal}
        loads = [load_group]

        # Define the boundary conditions
        restricted_degrees = [[self.nodes[0].index, 1, 1, 0, 0], [self.nodes[-1].index, 0, 1, 0, 0]]
        boundary_conditions = {'Restricted Degrees': restricted_degrees}

        # Calculate and assign the permanent impacts
        model = {'Nodes': structural_nodes, 'Beams': beams, 'Loads': loads,
                 'Boundary Conditions': boundary_conditions}
        d_tie, if_tie, rd_tie = structure_analysis(model, discType='Lengthwise', discLength=1)
        self.permanent_impacts = if_tie

        # Create the plots if needed
        if plots:
            plot_loads(model, 0, 'Tie permanent impacts')
            plot_internal_forces(model, d_tie, if_tie, 0, 'Moment', 'Tie permanent impacts')
        return
