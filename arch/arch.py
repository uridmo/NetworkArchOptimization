import numpy as np

from structureanalysis import structure_analysis
from structureanalysis.plotting import plot_internal_forces, plot_loads


class Arch:
    def __init__(self, span, rise, g, ea, ei, ga=0):
        self.span = span
        self.rise = rise
        self.nodes = []
        self.weight = g
        self.axial_stiffness = ea
        self.bending_stiffness = ei
        self.shear_stiffness = ga
        self.permanent_impacts = None

    def __len__(self):
        return len(self.nodes)-1

    def insert_node(self, nodes, x, y):
        node = nodes.add_node(x, y)
        if node not in self.nodes:
            for i in range(len(self.nodes)-1):
                if self.nodes[i].x < x < self.nodes[i+1].x:
                    self.nodes.insert(i+1, node)
                    break
        return node

    def arch_connection_nodes(self, nodes, hangers):
        for hanger in hangers:
            x_tie = hanger.tie_node.x
            angle = hanger.inclination

            for i in range(len(self.nodes) - 1):
                x_arch_1 = self.nodes[i].x
                x_arch_2 = self.nodes[i+1].x
                y_arch_1 = self.nodes[i].y
                y_arch_2 = self.nodes[i+1].y
                dx = x_arch_2 - x_arch_1
                dy = y_arch_2 - y_arch_1
                if angle == np.pi / 2:
                    if x_arch_1 < x_tie < x_arch_2:
                        x = x_tie
                        y = y_arch_1 + dy * (x_tie - x_arch_1) / dx
                        node = self.insert_node(nodes, x, y)
                        hanger.arch_node = node
                        break
                else:
                    tan_a = np.tan(angle)
                    a = -(dy * tan_a * x_tie - dy * tan_a * x_arch_1 + dx * tan_a * y_arch_1) / (dy - dx * tan_a)
                    b = -(y_arch_1 - tan_a * x_arch_1 + tan_a * x_tie) / (dy - dx * tan_a)
                    if 0 <= b < 1 and a > 0:
                        x = x_arch_1 + b * dx
                        y = y_arch_1 + b * dy
                        node = self.insert_node(nodes, x, y)
                        hanger.arch_node = node
                        break
        return

    def get_beams(self):
        n = len(self.nodes)
        beams_nodes = [[self.nodes[i].index, self.nodes[i + 1].index] for i in range(n - 1)]
        beams_stiffness = (n - 1) * [[self.axial_stiffness, self.bending_stiffness]]
        return beams_nodes, beams_stiffness

    def self_weight_loads(self, indices=range(0)):
        if not indices:
            indices = range(len(self))
        q = self.weight
        load_distributed = [[i, 0, 0, 0, -q, 0, 0, -q, 0] for i in indices]
        return load_distributed

    def calculate_permanent_impacts(self, nodes, hangers, n_0, mz_0, plots=False):
        n_arch = len(self.nodes)

        # Define the list of all nodes
        structural_nodes = nodes.structural_nodes()

        # Define the structural beams
        beams_nodes, beams_stiffness = self.get_beams()
        beams = {'Nodes': beams_nodes, 'Stiffness': beams_stiffness}

        # Apply self weight
        load_distributed = self.self_weight_loads(range(n_arch - 1))

        # Apply global self-stresses
        load_nodal = [[self.nodes[0].index, n_0, 0, mz_0], [self.nodes[-1].index, -n_0, 0, -mz_0]]

        # Apply hanger forces
        for hanger in hangers:
            node = hanger.arch_node.index
            vertical_force = -hanger.prestressing_force * np.sin(hanger.inclination)
            horizontal_force = -hanger.prestressing_force * np.cos(hanger.inclination)
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
        d_arch, if_arch, rd_arch = structure_analysis(model, discType='Lengthwise', discLength=1)
        self.permanent_impacts = if_arch

        # Create the plots if needed
        if plots:
            plot_loads(model, 0, 'Arch permanent impacts')
            plot_internal_forces(model, d_arch, if_arch, 0, 'Moment', 'Arch permanent impacts')
        return
