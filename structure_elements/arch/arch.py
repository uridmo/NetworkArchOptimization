import numpy as np
from matplotlib.patches import Polygon
import matplotlib.pyplot as plt

from structure_analysis import structure_analysis
from structure_analysis.plotting import plot_internal_forces, plot_loads
from structure_analysis.plotting.plotSettings import initialize_plot, adjustPlot, plotTitle
from structure_analysis.plotting.plotStructure import plotStructure
from structure_analysis.plotting.plotSupports import plot_supports
from structure_elements.line_element import LineElement


class Arch(LineElement):
    def __init__(self, span, rise, g, ea, ei, ga=0):
        super().__init__(g, ea, ei, ga=ga)
        self.span = span
        self.rise = rise
        return

    def arch_connection_nodes(self, nodes, hangers):
        for hanger in hangers.hangers:
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


    # def calculate_permanent_impacts(self, nodes, hangers, n_0, mz_0, plots=False):
    #     n_arch = len(self.nodes)
    #
    #     # Define the list of all nodes
    #     structural_nodes = nodes.structural_nodes()
    #
    #     # Define the structural beams
    #     beams_nodes, beams_stiffness = self.get_beams()
    #     beams = {'Nodes': beams_nodes, 'Stiffness': beams_stiffness}
    #
    #     # Apply self weight
    #     load_distributed = self.self_weight_loads(range(n_arch - 1))
    #
    #     # Apply global self-stresses
    #     load_nodal = [[self.nodes[0].index, n_0, 0, mz_0], [self.nodes[-1].index, -n_0, 0, -mz_0]]
    #
    #     # Apply hanger forces
    #     for hanger in hangers:
    #         node = hanger.arch_node.index
    #         vertical_force = -hanger.prestressing_force * np.sin(hanger.inclination)
    #         horizontal_force = -hanger.prestressing_force * np.cos(hanger.inclination)
    #         load_nodal.append([node, horizontal_force, vertical_force, 0])
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
    #     d_arch, if_arch, rd_arch = structure_analysis(model, discType='Lengthwise', discLength=1)
    #     self.permanent_impacts = if_arch
    #
    #     # Create the plots if needed
    #     if plots:
    #         plot_loads(model, 0, 'Arch permanent impacts')
    #         plot_internal_forces(model, d_arch, if_arch, 0, 'Moment', 'Arch permanent impacts')
    #     return
    #
    # def plot_internal_force(self, nodes, quantity, model=None, scale_max=0):
    #     # , title, show_extrema=False,
    #     #                  , scale_max=0.25):
    #
    #     color = 'orange'  # Color used if forces are shown
    #     max_color = 'red'  # Color used for max values
    #     min_color = 'blue'  # Color used for min values
    #
    #     nodes_location = nodes.structural_nodes()['Location']
    #     elements, a = self.get_beams()
    #
    #     x_min = min([node.x for node in nodes])
    #     x_max = max([node.x for node in nodes])
    #     z_min = min([node.y for node in nodes])
    #     z_max = max([node.y for node in nodes])
    #     diag_length = (((x_max - x_min) ** 2 + (z_max - z_min) ** 2) ** 0.5)
    #
    #     reactions = self.permanent_impacts[0][quantity]
    #     reaction_max = max([max(max(sublist), -min(sublist)) for sublist in reactions])
    #
    #     # Define scaling
    #     if max(reaction_max) > 1e-6:
    #         scale = diag_length / 12 / max(reaction_max, scale_max)
    #     else:
    #         scale = 0
    #
    #     # Define unit
    #     if quantity in ['Normal Force', 'Shear Force']:
    #         unit = 'kN'
    #     elif quantity == 'Moment':
    #         unit = 'kNm'
    #
    #     # Begin the plot
    #     fig, ax = initialize_plot()
    #
    #     if model:
    #         plotStructure(model, ax)
    #
    #     plotTitle(fig, quantity)
    #
    #     # Add the identifier for pos/neg values to the legend
    #     ax.plot(0, 0, color=max_color, label=quantity)
    #
    #     x_react = np.array([])
    #     y_react = np.array([])
    #
    #     # Cycle through elements
    #     for i, reaction in enumerate(reactions):
    #         start, end = elements[i][0], elements[i][1]
    #         x = np.linspace(nodes_location[start][0], nodes_location[end][0], num=len(reaction))
    #         y = np.linspace(nodes_location[start][1], nodes_location[end][1], num=len(reaction))
    #
    #         # Plot the combined x- and y-displacements if required
    #         values = np.array(reaction)
    #
    #         # Construct unit vector perpendicular to the corresponding element accoring to
    #         # sign convention
    #         dx = (nodes_location[end][0] - nodes_location[start][0])
    #         dy = (nodes_location[end][1] - nodes_location[start][1])
    #         dl = (dx**2 + dy**2)**0.5
    #
    #         normal_vec = [dy/dl, -dx/dl]
    #
    #         # absolute coordinates for displaying the values
    #         x_impact = x + normal_vec[0] * scale * values
    #         y_impact = y + normal_vec[1] * scale * values
    #
    #         if i == 0:
    #             x_arch = x
    #             y_arch = y
    #             x_react = x_impact
    #             y_react = y_impact
    #         else:
    #             x_arch = np.concatenate((x_arch, x))
    #             y_arch = np.concatenate((y_arch, y))
    #             x_react = np.concatenate((x_react, x_impact))
    #             y_react = np.concatenate((y_react, y_impact))
    #
    #     # Plot the impacts
    #     ax.plot(x_react, y_react, color=max_color, alpha=0.4)
    #
    #     # Fill it with a polygon
    #     x_fill = np.concatenate((x_react, x_arch[::-1]))
    #     y_fill = np.concatenate((y_react, y_arch[::-1]))
    #     xy_poly = np.stack((x_fill, y_fill))
    #     polygon = Polygon(np.transpose(xy_poly), edgecolor=None, fill=True, facecolor=color, alpha=0.5)
    #     ax.add_patch(polygon)
    #
    #     # plotLegend(ax)
    #     # plotHinges(model, ax)
    #     # plot_supports(model, ax)
    #     adjustPlot(ax)
    #     plt.show()
    #
    #     # if save_plot:
    #     #     if not os.path.isdir('Plots ' + title):
    #     #         os.makedirs('Plots ' + title)
    #     #
    #     #     plt.savefig('Plots ' + title + '/Loadgroup ' + str(load_group) + '_' + quantity + '.png', dpi=300,
    #     #                 bbox_inches='tight')
    #     return

