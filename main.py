import numpy as np

from hanger_arrangements import parallel_arrangement
from hanger_arrangements import radial_arrangement
from structural_analysis import hanger_forces_structure
from structural_analysis import get_hanger_forces


def main():
    s = 267.8
    r = 53.5
    q_tie = 178.1
    q_arch = 32.1
    n = 2
    alpha = np.radians(63.7)
    beta = np.radians(35)

    # hangers_0 = parallel_arrangement(s, n, alpha)
    hangers_1 = radial_arrangement(r, s, n, beta)
    model = hanger_forces_structure(hangers_1, s, q_tie, 1000000, 1)
    print(model)
    forces = get_hanger_forces(model)

    print(forces)
    print(q_tie * s)
    return


if __name__ == '__main__':
    main()
