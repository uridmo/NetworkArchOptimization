import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon


def plot_supports(model, ax, factor=0.03):
    """
    Takes the structure and the figure to plot on.
    
    structure['boundaryConditions'] is a matrix with columns [nodeNumber, x-translation, y-translation, rotation].
    Each movement is either restricted (1) or free (1)
    
    Plots the supports.
    """
    bc = model['Boundary Conditions']['Restricted Degrees']
    nodes = model['Nodes']['Location']

    # Dimensions of the structure
    x_max = max(node[0] for node in nodes)
    x_min = min(node[0] for node in nodes)
    y_max = max(node[1] for node in nodes)
    y_min = min(node[1] for node in nodes)
    dim_x, dim_y = x_max - x_min, y_max - y_min

    support_size = (max(dim_x, dim_y / 2) + max(dim_x / 2, dim_y)) * factor

    for i in range(len(bc)):
        # x and y coord. of current node
        x, y = nodes[bc[i][0]][0], nodes[bc[i][0]][1]

        # Supports for restricted rotation
        if bc[i][3] == 1:
            d = 0.3 * support_size
            solid_polygon = Polygon([[x + d, y + d], [x - d, y + d], [x - d, y - d], [x + d, y - d]],
                                    fill=True, color='black', alpha=1)
            ax.add_patch(solid_polygon)
            if bc[i][1] == 1 and bc[i][2] == 1:
                hatched_polygon = Polygon(
                    [[x - 2 * d, y - d], [x + 2 * d, y - d], [x + 2 * d, y - 2 * d], [x - 2 * d, y - 2 * d]],
                    fill=False, hatch='//////', edgecolor=None)
                ax.add_patch(hatched_polygon)
            if bc[i][1] == 1 and bc[i][2] == 0:
                ax.plot([x - 2 * d, x + 2 * d], [y - d, y - d], color='black')
                ax.plot([x - 2 * d, x + 2 * d], [y - 2 * d, y - 2 * d], color='black')

            if bc[i][1] == 0 and bc[i][2] == 1:
                ax.plot([x - d, x - d], [y - 2 * d, y + 2 * d], color='black')
                ax.plot([x - 2 * d, x - 2 * d], [y - 2 * d, y + 2 * d], color='black')

        # Supports for free rotation (Pin supports)
        poly_array = np.array([[0, 0],
                               [-0.5 * support_size, -np.sqrt(3) / 2 * support_size],
                               [+0.5 * support_size, -np.sqrt(3) / 2 * support_size]])
        pos = np.array([x, y])
        line = np.array([[+0.5 * support_size, -1.1 * support_size], [-0.5 * support_size, -1.1 * support_size]])

        if bc[i][3] == 0:
            if bc[i][1] == 1 and bc[i][2] == 1:
                poly = pos + poly_array
                support = Polygon(poly, fill=False, edgecolor='black')
                ax.add_patch(support)

                poly_line = pos + line
                poly2 = np.vstack((poly[1:], poly_line))
                support = Polygon(poly2, fill=True, color='black')
                ax.add_patch(support)

            else:
                if bc[i][1] == 1:
                    a = -np.pi/2
                else:
                    a = bc[i][4]

                c, s = np.cos(a), np.sin(a)
                r = np.array([[c, s], [-s, c]])

                poly = pos + poly_array @ r
                support = Polygon(poly, fill=False, edgecolor='black')
                ax.add_patch(support)

                line_1 = pos + line @ r
                ax.plot(line_1[:, 0], line_1[:, 1], color='black')
