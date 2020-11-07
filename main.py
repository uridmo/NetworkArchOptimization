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
    beta = np.radians(30)

    hanger_set = parallel_arrangement(span, n, alpha)
    hanger_set = radial_arrangement(rise, span, n, beta)
    hangers = mirror_hanger_set(hanger_set, span)

    model_tie = hanger_forces_structure(hangers, span, q_tie, 1000000, 1)
    d_tie, if_tie, rd_tie = structure_analysis(model_tie, discElements=10)
    plot_loads(model_tie, 0, 'Hello')
    plot_internal_forces(model_tie, d_tie, if_tie, 0, 'Moment', 'Hello 2')
    hanger_forces = get_hanger_forces(rd_tie)

    print(hanger_forces[0])
    print(hanger_forces[1])
    print(hanger_forces[2])
    print(min(hanger_forces[1]))
    print(sum(hanger_forces[2]))
    print(sum(hanger_forces[1]))
    print(q_tie * span)

    x, y = continuous_arch(span, rise, q_tie, 30, hanger_set)
    print(x)
    print(y)

    hangers, x_arch, y_arch = get_arch_nodes(x, y, hangers)
    print(hangers)
    print(x_arch)
    print(y_arch)

    model_arch = arch_structure(hangers, hanger_forces, x_arch, y_arch, 10000, 1000000)
    verify_input(model_arch)
    plot_loads(model_arch, 0, 'Hello')

    d_arch, if_arch, rd_arch = structure_analysis(model_arch, discElements=10)
    plot_internal_forces(model_arch, d_arch, if_arch, 0, 'Moment', 'Hello 2')
    plot_internal_forces(model_arch, d_arch, if_arch, 0, 'Normal Force', 'Hello 2')
    return


if __name__ == '__main__':
    main()
