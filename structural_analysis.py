import numpy as np
from copy import deepcopy



def tie_structure(hangers, s, q, ea, ei):
    n = len(hangers)
    positions = [h[0] for h in hangers]

    nodes_counter = 1
    nodes_location = [[0, 0]]
    restricted_degrees = [[0, 0, 1, 0, 0]]
    for i in range(n):
        x = positions[i]
        if i > 0 and x == positions[i - 1]:
            restricted_degrees[-1] = [nodes_counter-1, 1, 1, 0, 0]
        else:
            nodes_counter += 1
            nodes_location += [[x, 0]]
            restricted_degrees += [[nodes_counter-1, 0, 1, 0, -np.pi/2+hangers[i][1]]]
    nodes_counter += 1
    nodes_location += [[s, 0]]
    restricted_degrees += [[nodes_counter-1, 0, 1, 0, 0]]

    nodes = {'Location': nodes_location}

    beams_nodes = [[i, i + 1] for i in range(nodes_counter - 1)]
    beams_stiffness = [[ea, ei] for i in range(nodes_counter - 1)]
    beams = {'Nodes': beams_nodes, 'Stiffness': beams_stiffness}

    load_distributed = [[i, 0, 0, 0, -q, 0, 0, -q, 0] for i in range(nodes_counter - 1)]
    load_group = {'Distributed': load_distributed}
    loads = [load_group]

    boundary_conditions = {'Restricted Degrees': restricted_degrees}

    model = {'Nodes': nodes, 'Beams': beams, 'Loads': loads,
             'Boundary Conditions': boundary_conditions}
    return model


def arch_structure(hangers, hanger_forces, x_arch, y_arch, ea, ei):
    nodes_location = [[x_arch[i], y_arch[i]] for i in range(len(x_arch))]
    nodes = {'Location': nodes_location}

    beams_nodes = [[i, i + 1] for i in range(len(x_arch) - 1)]
    beams_stiffness = [[ea, ei] for i in range(len(x_arch) - 1)]
    beams = {'Nodes': beams_nodes, 'Stiffness': beams_stiffness}

    load_nodal = [[hangers[i][2], hanger_forces[2][i], -hanger_forces[1][i], 0] for i in range(len(hangers))]
    load_group = {'Nodal': load_nodal}
    loads = [load_group]

    restricted_degrees = [[0, 1, 1, 0, 0], [len(x_arch)-1, 1, 1, 0, 0]]
    boundary_conditions = {'Restricted Degrees': restricted_degrees}

    model = {'Nodes': nodes, 'Beams': beams, 'Loads': loads,
             'Boundary Conditions': boundary_conditions}
    return model


def get_hanger_forces(restricted_degrees_reaction):
    reactions = restricted_degrees_reaction[0]
    reactions = reactions[1:-1]
    forces = [r[2] for r in reactions]
    forces_v = [r[1] * np.sin(r[4]) + r[2] * np.cos(r[4]) for r in reactions]
    forces_h = [r[1] * np.cos(r[4]) + r[2] * np.sin(r[4]) for r in reactions]
    return forces, forces_v, forces_h


def network_arch_structure(model_tie, model_arch, hangers, ea, ei):
    nodes_location = deepcopy(model_tie['Nodes']['Location'])
    nodes_location += model_arch['Nodes']['Location'][1:-1]
    nodes = {'Location': nodes_location}

    n = len(model_tie['Nodes']['Location'])-1

    beams_nodes = deepcopy(model_tie['Beams']['Nodes'])
    beams_nodes += [[0, n+1]]
    beams_nodes += [[node[0]+n, node[1]+n] for node in model_arch['Beams']['Nodes'][1:-1]]
    beams_nodes += [[model_arch['Beams']['Nodes'][-1][0]+n, n]]
    beams_nodes += [[i+1, hangers[i][2]+n] for i in range(len(hangers))]

    beams_stiffness = deepcopy(model_tie['Beams']['Stiffness'])
    beams_stiffness += model_arch['Beams']['Stiffness']
    beams_stiffness += [[ea, ei] for i in hangers]
    beams = {'Nodes': beams_nodes, 'Stiffness': beams_stiffness}

    loads = [{}]

    restricted_degrees = [[0, 1, 1, 0, 0], [n, 0, 1, 0, 0]]
    boundary_conditions = {'Restricted Degrees': restricted_degrees}

    model = {'Nodes': nodes, 'Beams': beams, 'Loads': loads,
             'Boundary Conditions': boundary_conditions}
    return model
