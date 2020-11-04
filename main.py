import numpy as np
from structureanalysis import structure_analysis
from structureanalysis.plotting.plot_loads import plot_loads
from structureanalysis.plotting.plot_internal_forces import plot_internal_forces
from hanger_arrangements import parallel_arrangement
from hanger_arrangements import radial_arrangement
from hanger_arrangements import mirror_hanger_set
from structural_analysis import hanger_forces_structure
from structural_analysis import get_hanger_forces

from arch_construction import continuous_arch


def main():
    span = 267.8
    rise = 53.5
    q_tie = 178.1
    q_arch = 32.1
    n = 14
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
    reactions, vertical_reactions, horizontal_reactions = get_hanger_forces(rd_reaction)

    print(reactions)
    print(horizontal_reactions)
    print(vertical_reactions)
    print(min(vertical_reactions))
    print(sum(horizontal_reactions))
    print(sum(vertical_reactions))
    print(q_tie * span)

    y = continuous_arch(span, rise, q_tie, 10, hanger_set_0)
    print(y)
    return


if __name__ == '__main__':
    main()
