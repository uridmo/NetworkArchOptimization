import numpy as np




def get_normal_vectors(line_element, reactions):
    normal_vec = []
    for i, reaction in enumerate(reactions):
        x_start, x_end = line_element.nodes[i].x, line_element.nodes[i+1].x
        y_start, y_end = line_element.nodes[i].y, line_element.nodes[i+1].y

        dx = x_end - x_start
        dy = x_end - y_start
        dl = (dx ** 2 + dy ** 2) ** 0.5
        normal_vec.extend([[dy / dl, -dx / dl] for i in range(len(reaction))])
    normal_vec = np.array(normal_vec)
    return normal_vec


def get_value_list(reaction):
    values = []
    for i in range(len(reaction)):
        values.extend(reaction[i])
    values = np.array(values).transpose()
    return values


def get_value_list_2(reaction, reaction_2):
    values = []
    for i in range(len(reaction)):
        for j in range(len(reaction[i])):
            values.append(max(min(0, reaction_2[i][j]), reaction[i][j]))
    return values


# def get_min_max(element, nodes, reactions, reactions_2):
#     nodes_location = nodes.structural_nodes()['Location']
#     elements, k = element.get_beams()
#
#     r_max = [-inf for i in range(len(element.sections_set))]
#     x_max = [0 for i in range(len(element.sections_set))]
#     y_max = [0 for i in range(len(element.sections_set))]
#     r_min = [inf for i in range(len(element.sections_set))]
#     x_min = [0 for i in range(len(element.sections_set))]
#     y_min = [0 for i in range(len(element.sections_set))]
#
#     for i in range(len(reactions)):
#         start, end = elements[i][0], elements[i][1]
#         x = np.linspace(nodes_location[start][0], nodes_location[end][0], num=len(reactions[i]))
#         y = np.linspace(nodes_location[start][1], nodes_location[end][1], num=len(reactions[i]))
#
#         section = element.sections[i]
#         section_i = element.sections_set.index(section)
#
#         if max(reactions[i]) > r_max[section_i]:
#             r_max[section_i] = max(reactions[i])
#             i_max = reactions[i].index(r_max[section_i])
#             i_max = int(np.argmax(values))
#             r_max[section_i] = values[i_max]
#             x_max[section_i] = x_impact[i_max]
#             y_max[section_i] = y_impact[i_max]
#
#         if min(reactions_2[i]) < r_min[section_i]:
#             i_min = int(np.argmin(values))
#             r_min[section_i] = values[i_min]
#             x_min[section_i] = x_impact[i_min]
#             y_min[section_i] = y_impact[i_min]
#
#     return


def get_value_location(xy_coord, normal_vec, values, scale):
    values_2 = np.array((values,values)).transpose()
    xy_values = xy_coord + scale * values_2 * normal_vec
    return xy_values


