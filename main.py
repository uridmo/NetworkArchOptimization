import numpy as np
from structureanalysis import structure_analysis


def main():
    a: int = 10
    print(a)

    s: float = 267.8
    r: float = 53.5
    q_tie: float = 178.1
    q_arch: float = 32.1
    n = 13
    arrangement = "parallel"
    parameter = [63.7]
    arch_shape = "parabolic"

    hangers = define_hangers(s, n, arrangement, parameter)
    print(hangers)
    return


def get_hanger_forces():
    forces = 1
    return forces


def define_hangers(s, n, arrangement, parameter):
    if arrangement == "parallel":
        a = parameter[0]
        x = np.linspace(0, s, num=n + 1)
        positions = x[1:].tolist()
        angles = [a for i in range(n)]
    hangers = {"Position": positions, "Angles": angles}
    return hangers


if __name__ == '__main__':
    main()
