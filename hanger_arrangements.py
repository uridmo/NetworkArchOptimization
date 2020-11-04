import numpy as np
from numpy import linspace
from warnings import warn


def parallel_arrangement(s, n, alpha):
    x = linspace(0, s, num=n + 1, endpoint=False)
    positions = x[1:].tolist()
    angles = [alpha for i in range(n)]
    hanger_set = {"Position": positions, "Angles": angles}
    hangers = mirror_hanger_set(hanger_set, s)
    return hangers


def constant_change_arrangement(s, n, alpha_0, alpha_mid):
    x = linspace(0, s, num=n + 1, endpoint=False)
    positions = x[1:].tolist()
    da = alpha_0 - alpha_mid
    angles = [alpha_mid - da * (2 * x[i] - s) / s for i in range(n)]
    hanger_set = {"Position": positions, "Angles": angles}
    hangers = mirror_hanger_set(hanger_set, s)
    return hangers


def radial_arrangement(r, s, n, beta):
    radius = (r ** 2 + (s / 2) ** 2) / (2 * r)
    diag = (r ** 2 + (s / 2) ** 2) ** 0.5
    alpha = np.arcsin((diag / 2) / radius)

    angles_0 = linspace(-2 * alpha, 2 * alpha, num=2*(n+1)).tolist()
    angles_0 = angles_0[2::2]
    angles_1 = list(map(lambda x: np.pi/2 - x - beta, angles_0))

    pos_arch_x = [radius * np.sin(angles_0[i]) for i in range(n)]
    pos_arch_y = [r - radius + radius * np.cos(angles_0[i]) for i in range(n)]

    pos_tie_x = [s / 2 + pos_arch_x[i] - pos_arch_y[i] / np.tan(angles_1[i]) for i in range(n)]

    # Check whether the hangers do not cross each other
    checks = [pos_tie_x[i] > pos_tie_x[i + 1] for i in range(n - 1)]
    if any(checks):
        warn("Some hangers cross each other")

    # Check whether all hangers lie on the tie
    kicks = 0
    for i in range(n):
        if pos_tie_x[i - kicks] < 0:
            pos_tie_x.pop(i - kicks)
            angles_1.pop(i - kicks)
            kicks += 1
            warn("The " + str(i) + ". hanger of the set was deleted as it lies outside the tie")

    hanger_set = {"Position": pos_tie_x, "Angles": angles_1}
    hangers = mirror_hanger_set(hanger_set, s)
    return hangers


def mirror_hanger_set(hanger_set, s):
    hangers = hanger_set
    hangers['Position'] += list(map(lambda x: s-x, hanger_set['Position']))
    hangers['Angles'] += list(map(lambda x: np.pi-x, hanger_set['Angles']))
    array_sort = [(hangers['Position'][i], hangers['Angles'][i]) for i in range(len(hangers['Position']))]
    array_sort.sort(key=lambda x: x[0])
    hangers['Position'] = [hanger[0] for hanger in array_sort]
    hangers['Angles'] = [hanger[1] for hanger in array_sort]
    return hangers
