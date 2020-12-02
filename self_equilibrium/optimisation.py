import numpy as np
from scipy import optimize

from self_equilibrium.static_analysis import zero_displacement


def optimize_self_stresses(arch, tie, nodes, hangers, hanger_range=(0.7, 1.3), n_range=(-np.inf, np.inf)):
    a, b = get_self_stress_matrix(nodes, hangers, arch=arch, tie=tie, factors=(1, 1.5))
    ones = np.ones_like(np.expand_dims(b, axis=1))
    a_ub = np.vstack((np.hstack((-ones, -a)), np.hstack((-ones, a))))
    b_ub = np.array(list(b) + list(-b))
    c = np.array([1] + [0 for i in range(a.shape[1])])

    weight = tie.weight()
    sine_sum = 0
    for hanger in hangers:
        sine_sum += np.sin(hanger.inclination)
    force = weight / sine_sum
    n = len(hangers.hanger_sets[0].hangers)
    force_range = (hanger_range[0]*force, hanger_range[1]*force)

    inf_range = (-np.inf, np.inf)
    bounds = [inf_range, n_range, inf_range] + [force_range]*n
    sol = optimize.linprog(c, A_ub=a_ub, b_ub=b_ub, bounds=bounds, method='revised simplex')  # , x0=x0)

    x = sol.x
    hangers.set_prestressing_forces(x[3:])
    n_0, m_z0 = x[1], x[2]
    return n_0, m_z0


def optimize_self_stresses_tie(tie, nodes, hangers, hanger_range=(0.7, 1.3)):
    a, b = get_self_stress_matrix(nodes, hangers, tie=tie)
    ones = np.ones_like(np.expand_dims(b, axis=1))
    a = np.delete(a, 0, 1)
    a_ub = np.vstack((np.hstack((-ones, -a)), np.hstack((-ones, a))))
    c = np.array([1] + [0 for i in range(a.shape[1])])
    b_ub = np.array(list(b) + list(-b))

    weight = tie.weight()
    sine_sum = 0
    for hanger in hangers:
        sine_sum += np.sin(hanger.inclination)
    force = weight / sine_sum
    n = len(hangers.hanger_sets[0].hangers)
    inf_range = (-np.inf, np.inf)
    force_range = (hanger_range[0]*force, hanger_range[1]*force)
    bounds = [inf_range]*2 + [force_range]*n
    sol = optimize.linprog(c, A_ub=a_ub, b_ub=b_ub, bounds=bounds, method='revised simplex')
    x = sol.x

    mz_0 = x[1]
    hangers.set_prestressing_forces(x[2:])
    hangers.assign_permanent_effects()
    return mz_0


def get_self_stress_matrix(nodes, hangers, arch=None, tie=None, factors=(1, 1)):
    n = 2 + len(hangers.get_hanger_forces(i=0))
    x = [0 for i in range(n)]
    b = moment_distribution(nodes, hangers, x, arch=arch, tie=tie, factors=factors)

    a = []
    for i in range(n):
        x[i] = 1
        moment_i = moment_distribution(nodes, hangers, x, arch=arch, tie=tie, factors=factors)
        a.append(list(moment_i - b))
        x[i] = 0
    a = np.array(a).transpose()
    return a, b


def moment_distribution(nodes, hangers, x, arch=None, tie=None, factors=(1, 1)):
    if arch:
        if tie:
            moment_arch = moment_distribution_arch(x, nodes, hangers, arch, factor=factors[0])
            moment_tie = moment_distribution_tie(x, nodes, hangers, tie, factor=factors[1])
            moment = np.concatenate((moment_arch, moment_tie))
        else:
            moment = moment_distribution_arch(x, nodes, hangers, arch, factor=factors[0])
    else:
        moment = moment_distribution_tie(x, nodes, hangers, tie, factor=factors[1])
    return moment


def moment_distribution_arch(x, nodes, hangers, arch, factor=1):
    hangers.set_prestressing_forces(x[2:])
    arch.assign_permanent_effects(nodes, hangers, x[0], -x[1])
    moment_arch = arch.effects['Permanent']['Moment']
    moment_arch *= factor
    return moment_arch


def moment_distribution_tie(x, nodes, hangers, tie, factor=1):
    hangers.set_prestressing_forces(x[2:])
    tie.assign_permanent_effects(nodes, hangers, -x[0], x[1])
    moment_tie = tie.effects['Permanent']['Moment']
    moment_tie *= factor
    return moment_tie


def blennerhassett_forces(arch, tie, nodes, hangers):
    forces = np.array([2420, 2015, 2126, 2051, 1766, 1931, 1877, 1784, 1757, 1646, 1601, 2371, 1842])

    a, b = get_self_stress_matrix(arch, tie, nodes, hangers)
    mod = np.zeros((a.shape[1], 3))
    mod[0, 0] = 1
    mod[1, 1] = 1
    mod[2:, 2] = forces
    ones = np.ones_like(np.expand_dims(b, axis=1))
    a_ub = np.vstack((np.hstack((-ones, -a @ mod)), np.hstack((-ones, a @ mod))))
    b_ub = np.array(list(b) + list(-b))
    c = np.array([1] + [0 for i in range(3)])
    bounds = [(-np.inf, np.inf) for i in range(3)] + [(0.8, 1.2)]
    sol = optimize.linprog(c, A_ub=a_ub, b_ub=b_ub, bounds=bounds, method='revised simplex')  # , x0=x0)
    x = sol.x

    hangers.set_prestressing_forces(list(x[3] * forces))
    hangers.assign_permanent_effects()
    arch.assign_permanent_effects(nodes, hangers, x[1], -x[2])
    tie.assign_permanent_effects(nodes, hangers, -x[1], x[2])
    return
