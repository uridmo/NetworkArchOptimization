import numpy as np
from matplotlib.patches import Arc, FancyArrow


def plot_loads(model, i, ax, arrows_amount=30):
    """
    Takes the structure and load dictionary.

    Displays the structure with the user defined loads

    TO DO: display of forced rotations
    """
    # Settings
    # ------------------------------------
    force_color = 'red'
    moment_color = 'blue'
    # ------------------------------------

    nodes = model['Nodes']['Location']
    elements = model['Beams']['Nodes']
    loads = model['Loads'][i]

    loads_nodal = loads['Nodal'] if 'Nodal' in loads else []
    loads_point = loads['Point'] if 'Point' in loads else []
    loads_line = loads['Distributed'] if 'Distributed' in loads else []

    # Determine Scaling Factors
    # ------------------------------------

    x_min = min([node[0] for node in nodes])
    x_max = max([node[0] for node in nodes])
    z_min = min([node[1] for node in nodes])
    z_max = max([node[1] for node in nodes])
    length = (((x_max - x_min) ** 2 + (z_max - z_min) ** 2) ** 0.5)

    # scaleDisplacements = 20
    max_nodal = max([max(abs(load_nodal[1]), abs(load_nodal[2])) for load_nodal in loads_nodal] + [0])
    max_point = max([max(abs(load_point[2]), abs(load_point[3])) for load_point in loads_point] + [0])
    max_force = max(max_point, max_nodal, 0.0001)
    max_length = length / 10
    min_length = length / 18

    max_distributed = max([max(abs(load_line[3]), abs(load_line[6]),
                               abs(load_line[4]), abs(load_line[7]),
                               abs(load_line[5]), abs(load_line[8])) for load_line in loads_line] + [0])

    scale_distributed_forces = length / 24 / max(max_distributed, 0.0001)

    # Plot nodal Forces
    for i in range(len(loads_nodal)):
        force = max((loads_nodal[i][1]**2 + loads_nodal[i][2]**2)**0.5, 1)
        f_x = loads_nodal[i][1]/force * max(force / max_force * max_length, min_length)
        f_y = loads_nodal[i][2]/force * max(force / max_force * max_length, min_length)
        m_z = loads_nodal[i][3]

        target_x = nodes[loads_nodal[i][0]][0]
        target_y = nodes[loads_nodal[i][0]][1]

        if (abs(f_x) + abs(f_y)) > 0:
            if loads_nodal[i][-1]==[]:
                arrow = FancyArrow(target_x, target_y, f_x, f_y, length_includes_head=True,
                                   head_width=3, linewidth=2, color=force_color, zorder=10)
            else:
                arrow = FancyArrow(target_x-f_x, target_y-f_y, f_x, f_y, length_includes_head=True,
                                   head_width=3, linewidth=2, color=force_color, zorder=10)
            ax.add_patch(arrow)
        if m_z != 0:
            # ax.plot(target_x, target_y, marker='o', markersize=4, alpha=1, color=moment_color)
            if m_z > 0:
                arc = Arc((target_x, target_y), 20, 20, 0, 180, 45, linewidth=2, color=moment_color, zorder=5)
                ax.add_patch(arc)
                arrow = FancyArrow(target_x + 0.35255*20, target_y + 0.35305*20, -0.007*30, +0.01*30, length_includes_head=True,
                                   head_width=3, linewidth=2, color=moment_color, zorder=5)
            else:
                arc = Arc((target_x, target_y), 20, 20, 0, 135, 0, linewidth=2, color=moment_color, zorder=5)
                ax.add_patch(arc)
                arrow = FancyArrow(target_x - 0.35255*20, target_y + 0.35305*20, +0.007*30, +0.01*30, length_includes_head=True,
                                   head_width=3, linewidth=2, color=moment_color, zorder=5)
            ax.add_patch(arrow)

    # Plot point forces
    for j in range(len(loads_point)):
        i = loads_point[j][0]
        element_vector = [nodes[elements[i][1]][0] - nodes[elements[i][0]][0],
                          nodes[elements[i][1]][1] - nodes[elements[i][0]][1]]
        element_vector = element_vector / np.linalg.norm(element_vector)

        loc = loads_point[j][1]
        target_x = nodes[elements[i][0]][0] + loc * element_vector[0]
        target_y = nodes[elements[i][0]][1] + loc * element_vector[1]

        f_x = np.sign(loads_point[j][2]) * max(abs(loads_point[j][2]) / max_force * max_length, min_length)
        f_y = np.sign(loads_point[j][3]) * max(abs(loads_point[j][3]) / max_force * max_length, min_length)
        m_z = loads_point[i][4]

        if (abs(f_x) + abs(f_y)) > 0:
            arrow = FancyArrow(target_x-f_x, target_y-f_y, f_x, f_y, length_includes_head=True,
                               head_width=3, linewidth=2, color=force_color, zorder=10)
            ax.add_patch(arrow)
        if m_z != 0:
            ax.plot(target_x, target_y, marker='o', markersize=4, alpha=1, color=moment_color)

            if m_z > 0:
                arc = Arc((target_x, target_y), 1, 1, 0, 240, 110, linewidth=2, color=moment_color, zorder=5)
                ax.add_patch(arc)
                arrow = FancyArrow(target_x - 0.35255, target_y + 0.35405, -0.01, -0.005, length_includes_head=True,
                                   head_width=3, linewidth=0.5, color=moment_color, zorder=5)
            else:
                arc = Arc((target_x, target_y), 1, 1, 0, 70, 300, linewidth=2, color=moment_color, zorder=5)
                ax.add_patch(arc)
                arrow = FancyArrow(target_x + 0.35255, target_y + 0.35405, +0.01, -0.005, length_includes_head=True,
                                   head_width=3, linewidth=0.5, color=moment_color, zorder=5)
            ax.add_patch(arrow)


    # Plot line loads
    for j in range(len(loads_line)):
        i = loads_line[j][0]
        element_vector = [nodes[elements[i][1]][0] - nodes[elements[i][0]][0],
                          nodes[elements[i][1]][1] - nodes[elements[i][0]][1]]
        element_vector = element_vector / np.linalg.norm(element_vector)

        l_start = loads_line[j][1]
        l_end = loads_line[j][2]
        qx_start = loads_line[j][3] * scale_distributed_forces
        qy_start = loads_line[j][4] * scale_distributed_forces
        qx_end = loads_line[j][6] * scale_distributed_forces
        qy_end = loads_line[j][7] * scale_distributed_forces

        if qx_start != 0 or qy_start != 0 or qx_end != 0 or qy_end != 0:
            target_x_start = nodes[elements[i][0]][0] + element_vector[0] * l_start
            target_x_end = nodes[elements[i][0]][0] + element_vector[0] * l_end
            target_y_start = nodes[elements[i][0]][1] + element_vector[1] * l_start
            target_y_end = nodes[elements[i][0]][1] + element_vector[1] * l_end

            x = [target_x_end - qx_end, target_x_start - qx_start]
            y = [target_y_end - qy_end, target_y_start - qy_start]
            ax.plot(x, y, color=force_color, linewidth=1.3)

            # draw Arrows
            amount = int((l_end - l_start) / (length / arrows_amount) + 2)
            for k in range(amount):
                loc = l_start + (l_end - l_start) * k / (amount - 1)
                x = nodes[elements[i][0]][0] + element_vector[0] * loc
                y = nodes[elements[i][0]][1] + element_vector[1] * loc
                arrow_length_x = (l_end - loc) / (l_end - l_start) * qx_start + (loc - l_start) / (l_end - l_start) * qx_end
                arrow_length_y = (l_end - loc) / (l_end - l_start) * qy_start + (loc - l_start) / (l_end - l_start) * qy_end
                if abs(arrow_length_x) > length / 100 or abs(arrow_length_y) > length / 100:
                    arrow = FancyArrow(x - arrow_length_x, y - arrow_length_y, arrow_length_x, arrow_length_y,
                                       length_includes_head=True,
                                       head_width=4, linewidth=1, color=force_color, zorder=5)
                    ax.add_patch(arrow)




    return ax
