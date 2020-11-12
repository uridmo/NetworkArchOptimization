import numpy as np
from matplotlib.patches import Polygon

from structure_analysis import structure_analysis
from structure_analysis.plotting import plot_loads, plot_internal_forces


class LineElement:
    def __init__(self, g, ea, ei, ga=0):
        self.nodes = []
        self.sections = []
        self.weight = g
        self.axial_stiffness = ea
        self.bending_stiffness = ei
        self.shear_stiffness = ga
        self.impacts = {}  # Maybe create class
        self.impacts_max = {}
        return

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

        # Define the structural beams
        beams_nodes, beams_stiffness = self.beams()
        beams = {'Nodes': beams_nodes, 'Stiffness': beams_stiffness}

        # Apply self weight
        load_distributed = self.self_weight()

        # Apply global self-stresses
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

        # Define the boundary conditions
        restricted_degrees = [[self.nodes[0].index, 1, 1, 0, 0], [self.nodes[-1].index, 0, 1, 0, 0]]
        boundary_conditions = {'Restricted Degrees': restricted_degrees}

        # Calculate and assign the permanent impacts
        model = {'Nodes': structural_nodes, 'Beams': beams, 'Loads': loads,
                 'Boundary Conditions': boundary_conditions}
        d, i_f, rd = structure_analysis(model, discType='Lengthwise', discLength=1)
        self.impacts['Permanent'] = i_f[0]

        # Create the plots if needed
        if plots:
            plot_loads(model, 0, 'Tie permanent impacts')
            plot_internal_forces(model, d, i_f, 0, 'Moment', 'Tie permanent impacts')
        return

    def plot_internal_force(self, ax, nodes, impact, scale_max=0, color_line='red', color_fill='orange'):
        nodes_location = nodes.structural_nodes()['Location']
        elements, k = self.beams()

        x_min = min([node.x for node in nodes])
        x_max = max([node.x for node in nodes])
        z_min = min([node.y for node in nodes])
        z_max = max([node.y for node in nodes])
        diag_length = (((x_max - x_min) ** 2 + (z_max - z_min) ** 2) ** 0.5)

        if type(impact) is str:
            reactions = self.impacts[impact]
        else:
            reactions = impact

        reaction_max = max([max(max(sublist), -min(sublist)) for sublist in reactions])

        # Define scaling
        if reaction_max > 1e-6:
            scale = diag_length / 12 / max(reaction_max, scale_max)
        else:
            scale = 0

        x_arch = np.array([])
        y_arch = np.array([])
        x_react = np.array([])
        y_react = np.array([])

        # Cycle through elements
        for i, reaction in enumerate(reactions):
            start, end = elements[i][0], elements[i][1]
            x = np.linspace(nodes_location[start][0], nodes_location[end][0], num=len(reaction))
            y = np.linspace(nodes_location[start][1], nodes_location[end][1], num=len(reaction))

            # Plot the combined x- and y-displacements if required
            values = np.array(reaction)

            # Construct unit vector perpendicular to the corresponding element accoring to
            # sign convention
            dx = (nodes_location[end][0] - nodes_location[start][0])
            dy = (nodes_location[end][1] - nodes_location[start][1])
            dl = (dx**2 + dy**2)**0.5

            normal_vec = [dy/dl, -dx/dl]

            # Absolute coordinates for displaying the values
            x_impact = x + normal_vec[0] * scale * values
            y_impact = y + normal_vec[1] * scale * values

            # Append the arrays
            x_arch = np.append(x_arch, x)
            y_arch = np.append(y_arch, y)
            x_react = np.append(x_react, x_impact)
            y_react = np.append(y_react, y_impact)

        # Plot the impacts
        ax.plot(x_react, y_react, color=color_line, alpha=0.4)

        # Fill it with a polygon
        x_fill = np.concatenate((x_react, x_arch[::-1]))
        y_fill = np.concatenate((y_react, y_arch[::-1]))
        xy_poly = np.stack((x_fill, y_fill))
        polygon = Polygon(np.transpose(xy_poly), edgecolor=None, fill=True, facecolor=color_fill, alpha=0.5)
        ax.add_patch(polygon)
        return
