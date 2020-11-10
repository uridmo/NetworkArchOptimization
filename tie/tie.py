import numpy as np

from structureanalysis import structure_analysis
from structureanalysis.plotting import plot_loads
from structureanalysis.plotting import plot_internal_forces


class Tie:
    def __init__(self, nodes, span, hangers):
        self.span = span
        self.start_node = nodes.add_node(0, 0)
        self.end_node = nodes.add_node(span, 0)

        hangers.hangers.sort(key=lambda n: n.tie_node.x)

        self.middle_nodes = []
        self.middle_nodes_hangers = []
        for hanger in hangers.hangers:
            if hanger.tie_node not in self.middle_nodes:
                self.middle_nodes += [hanger.tie_node]
                self.middle_nodes_hangers += [[hanger]]
            else:
                i = self.middle_nodes.index(hanger.tie_node)
                self.middle_nodes_hangers[i].append(hanger)

        self.nodes = [self.start_node] + self.middle_nodes + [self.end_node]

        self.hangers = hangers
        self.bending_stiffness = None
        self.axial_stiffness = None
        self.shear_stiffness = None
        self.permanent_impacts = None

    def assign_stiffness(self, ea, ei, ga=0):
        self.axial_stiffness = ea
        self.bending_stiffness = ei
        self.shear_stiffness = ga
        return

    def calculate_permanent_impacts(self, nodes, q, mz, plots=False):
        n = len(self.nodes)

        structural_nodes = nodes.structural_nodes()

        beams_nodes = [[self.nodes[i].index, self.nodes[i + 1].index] for i in range(n - 1)]
        beams_stiffness = (n - 1) * [[self.axial_stiffness, self.bending_stiffness]]
        beams = {'Nodes': beams_nodes, 'Stiffness': beams_stiffness}

        load_distributed = [[i, 0, 0, 0, -q, 0, 0, -q, 0] for i in range(n - 1)]
        load_nodal = [[self.start_node.index, 0, 0, -mz], [self.end_node.index, 0, 0, mz]]
        for hanger in self.hangers:
            node = hanger.tie_node.index
            vertical_force = hanger.prestressing_force*np.sin(hanger.inclination)
            horizontal_force = hanger.prestressing_force*np.cos(hanger.inclination)
            load_nodal.append([node, horizontal_force, vertical_force, 0])
        load_group = {'Distributed': load_distributed, 'Nodal': load_nodal}
        loads = [load_group]

        restricted_degrees = [[self.start_node.index, 1, 1, 0, 0], [self.end_node.index, 0, 1, 0, 0]]
        boundary_conditions = {'Restricted Degrees': restricted_degrees}

        model = {'Nodes': structural_nodes, 'Beams': beams, 'Loads': loads,
                 'Boundary Conditions': boundary_conditions}

        d_tie, if_tie, rd_tie = structure_analysis(model, discType='Lengthwise', discLength=1)
        self.permanent_impacts = if_tie

        if plots:
            plot_loads(model, 0, 'Hello')
            plot_internal_forces(model, d_tie, if_tie, 0, 'Moment', 'Hello 2')

        return
