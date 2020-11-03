import numpy as np
from structureanalysis import structure_analysis
from structureanalysis.plotting import plot_internal_forces
from scipy.sparse import SparseEfficiencyWarning
from contextlib import suppress
from hanger_arrangements import parallel_arrangement
from structure_definition import hanger_forces_structure


def main():
    s: float = 267.8
    r: float = 53.5
    q_tie: float = 178.1
    q_arch: float = 32.1
    n = 13
    alpha = 63.7
    arch_shape = "parabolic"

    hangers = parallel_arrangement(s, n, alpha)

    hangers_forces = get_hanger_forces(s, n, hangers, q_tie, 100, 10000)
    print(hangers_forces)
    vertical_reactions = [reaction[1] * np.sin(reaction[4]) + reaction[2] * np.cos(reaction[4]) for reaction in
                          hangers_forces[0]]
    horizontal_reactions = [reaction[1] * np.cos(reaction[4]) + reaction[2] * np.sin(reaction[4]) for reaction in
                            hangers_forces[0]]
    print(q_tie * s)
    print(sum(vertical_reactions))
    print(sum(horizontal_reactions))
    return


def get_hanger_forces(s, n, hangers, q, ea, ei):
    nodes_location = [[x, 0] for x in hangers["Position"]]
    nodes_location = [[0, 0]] + nodes_location + [[s, 0]]
    print(nodes_location)
    nodes = {'Location': nodes_location}

    beams_nodes = [[i, i + 1] for i in range(n + 1)]
    beams_stiffness = [[ea, ei] for i in range(n + 1)]
    beams = {'Nodes': beams_nodes, 'Stiffness': beams_stiffness}

    load_distributed = [[i, 0, 0, 0, -q, 0, 0, -q, 0] for i in range(n + 1)]
    load_group = {'Distributed': load_distributed}
    loads = [load_group]

    restricted_degrees = [[i + 1, 0, 1, 0, -0.5] for i in range(n + 1)]
    restricted_degrees = [[0, 0, 1, 0, 0]] + restricted_degrees
    print(restricted_degrees)
    boundary_conditions = {'Restricted Degrees': restricted_degrees}

    model = {'Nodes': nodes, 'Beams': beams, 'Loads': loads,
             'Boundary Conditions': boundary_conditions}
    with suppress(SparseEfficiencyWarning):
        displacements, internal_forces, restricted_degrees_reaction = structure_analysis(model, discElements=10)

    plot_internal_forces(model, displacements, internal_forces)
    return restricted_degrees_reaction


def define_hangers(s, n, arrangement, parameter):
    if arrangement == "parallel":
        a = parameter[0]
        x = np.linspace(0, s, num=n + 1, endpoint=False)
        positions = x[1:].tolist()
        angles = [a for i in range(n)]
    hangers = {"Position": positions, "Angles": angles}
    return hangers


if __name__ == '__main__':
    main()
