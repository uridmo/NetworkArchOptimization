import numpy as np
from structureanalysis import structure_analysis
from structureanalysis import verify_input
from structureanalysis.plotting.plot_loads import plot_loads
from structureanalysis.plotting.plot_internal_forces import plot_internal_forces
from hanger_arrangements import parallel_arrangement
from hanger_arrangements import radial_arrangement
from hanger_arrangements import mirror_hanger_set
from structural_analysis import hanger_forces_structure
from structural_analysis import get_hanger_forces
from structural_analysis import arch_structure

from arch_construction import continuous_arch
from arch_construction import get_arch_nodes


def main():
    span = 267.8
    rise = 53.5
    q_tie = 178.1
    q_arch = 32.1
    n = 15
    alpha = np.radians(45)
    beta = np.radians(35)

    hanger_set_0 = parallel_arrangement(span, n, alpha)
    hangers_0 = mirror_hanger_set(hanger_set_0, span)

    hanger_set_1 = radial_arrangement(rise, span, n, beta)
    hangers_1 = mirror_hanger_set(hanger_set_1, span)

    model = hanger_forces_structure(hangers_1, span, q_tie, 1000000, 1)
    displacements, internal_forces, rd_reaction = structure_analysis(model, discElements=10)
    plot_loads(model, 0, 'Hello')
    plot_internal_forces(model, displacements, internal_forces, 0, 'Moment', 'Hello 2')
    hanger_forces = get_hanger_forces(rd_reaction)

    print(hanger_forces[0])
    print(hanger_forces[1])
    print(hanger_forces[2])
    print(min(hanger_forces[1]))
    print(sum(hanger_forces[2]))
    print(sum(hanger_forces[1]))
    print(q_tie * span)

    x, y = continuous_arch(span, rise, q_tie, 50, hanger_set_0)
    print(x)
    print(y)

    hangers, x_arch, y_arch = get_arch_nodes(x, y, hangers_0)
    print(hangers)
    print(x_arch)
    print(y_arch)

    model_2 = arch_structure(hangers, hanger_forces, x_arch, y_arch, 10000, 1000000)
    verify_input(model_2)
    plot_loads(model_2, 0, 'Hello')

    displacements_2, internal_forces_2, rd_reaction_2 = structure_analysis(model_2, discElements=10)
    plot_internal_forces(model_2, displacements_2, internal_forces_2, 0, 'Moment', 'Hello 2')
    plot_internal_forces(model_2, displacements_2, internal_forces_2, 0, 'Normal Force', 'Hello 2')
    return


if __name__ == '__main__':
    main()
