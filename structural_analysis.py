import numpy as np
from structureanalysis import structure_analysis
from structureanalysis.plotting import plot_internal_forces
from scipy.sparse import SparseEfficiencyWarning
from contextlib import suppress


def hanger_forces_structure(hangers, s, q, ea, ei):
    n = len(hangers["Position"])
    positions = [round(i, 6) for i in hangers['Position']]

    nodes_counter = 1
    nodes_location = [[0, 0]]
    restricted_degrees = [[0, 1, 1, 0, 0]]
    for i in range(n):
        x = positions[i]
        if i > 0 and x == positions[i - 1]:
            restricted_degrees[-1] = [nodes_counter-1, 1, 1, 0, 0]
        else:
            nodes_counter += 1
            nodes_location += [[x, 0]]
            restricted_degrees += [[nodes_counter-1, 0, 1, 0, -np.pi/2+hangers['Angles'][i]]]
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


def get_hanger_forces(model):
    with suppress(SparseEfficiencyWarning):
        displacements, internal_forces, restricted_degrees_reaction = structure_analysis(model, discElements=10)
    hangers_forces = restricted_degrees_reaction[0]
    print(hangers_forces)
    plot_internal_forces(model, displacements, internal_forces)

    reactions = [r[2] for r in hangers_forces]
    vertical_reactions = [r[1] * np.sin(r[4]) + r[2] * np.cos(r[4]) for r in hangers_forces]
    horizontal_reactions = [r[1] * np.cos(r[4]) + r[2] * np.sin(r[4]) for r in hangers_forces]
    return reactions


def network_arch_bridge():
    model = 0
    return model
