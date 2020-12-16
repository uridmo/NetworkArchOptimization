import numpy as np
from scipy.optimize import fsolve
from structure_elements.arch.arch import Arch


class ContinuousArch(Arch):
    def __init__(self, nodes, hanger_set, g_arch, g_tie, span, rise, n=100):
        super().__init__(nodes, span, rise)

        a_x = [hanger.tie_node.x for hanger in hanger_set.hangers]
        angles = [hanger.inclination for hanger in hanger_set.hangers]

        # a_x = [a_x[0]/2-0.1] + [a_x[0]/2] + a_x + [span/2 + a_x[-1]/2] + [span/2 + a_x[-1]/2 + 0.1]
        # angles = [np.pi-0.001] + [angles[0]] + angles + [angles[-1]] + [0.001]

        n_peak_0 = (g_arch + g_tie) * span ** 2 / 8 / rise
        x_arch = np.linspace(span / 2, span, n + 1)

        # Function giving the interpolated angle of the first hanger-set at x
        def fun_angle(x): return np.interp(x, a_x, angles)

        def fun_height(x, angle, h): return x + h / np.tan(angle)

        def fun_height_2(x, h): return fun_height(x, fun_angle(x), h)

        # Find hangers that reach the crown of the arch
        l0 = fsolve(lambda l: (fun_height_2(l, rise) - span / 2), np.array([0]))

        sol = fsolve(lambda x: thrust_line_by_n_peak(x, x_arch, rise, span, l0, g_tie, g_arch,
                                                     fun_angle, fun_height_2)[0], n_peak_0)
        n_peak = sol[0]
        [y_arch, nx] = thrust_line_by_n_peak(n_peak, x_arch, rise, span, l0, g_tie, g_arch,
                                             fun_angle, fun_height_2)[1:3]

        # Mirror the obtained shape
        x_arch = list(np.linspace(0, span, 2 * n + 1))
        y_arch = y_arch.tolist()
        y_arch = y_arch[-1:0:-1] + y_arch

        self.tie_tension = nx[-1]
        for i in range(len(x_arch)):
            self.insert_node(nodes, x_arch[i], y_arch[i])
        return


def thrust_line_by_n_peak(n_peak, x_arch, rise, span, l0, g_tie, g_arch, fun_angle, fun_height_2):
    nx_arr = np.zeros(len(x_arch))
    ny_arr = np.zeros(len(x_arch))
    y = np.zeros(len(x_arch))
    l1 = np.zeros(len(x_arch))
    l2 = np.zeros(len(x_arch))
    dx = np.diff(x_arch)

    nx_arr[0] = n_peak
    y[0] = rise
    l1[0] = l0
    l2[0] = l0
    dy = np.array([0.1])

    for i in range(len(x_arch) - 1):
        dy = fsolve(lambda d: thrust_line_step(d, g_tie, g_arch, span, nx_arr[i], ny_arr[i], x_arch[i], y[i],
                                               dx[i], l1[i], l2[i], fun_angle, fun_height_2)[0], dy, factor=0.1)[0]
        [nx, ny, dl1, dl2] = thrust_line_step(dy, g_tie, g_arch, span, nx_arr[i], ny_arr[i], x_arch[i],
                                              y[i], dx[i], l1[i], l2[i], fun_angle, fun_height_2)[1:]
        y[i + 1] = y[i] - dy
        l1[i + 1] = l1[i] + dl1
        l2[i + 1] = l2[i] - dl2
        nx_arr[i + 1] = nx
        ny_arr[i + 1] = ny
    dy = y[-1]
    return dy, y, nx_arr, ny_arr, l1, l2


def thrust_line_step(dy, g_tie, g_arch, s, nx, ny, x, y, dx, l1, l2, fun_angle, fun_height_2):
    dl1 = fsolve(lambda z: fun_height_2(l1 + z, y - dy) - (x + dx), np.array([0]))[0]
    dl2 = fsolve(lambda z: fun_height_2(l2 - z, y - dy) - (s - x - dx), np.array([0]))[0]

    a1 = fun_angle(l1 + dl1 / 2)
    b1 = fun_angle(s - (l1 + dl1 / 2))
    a2 = fun_angle(l2 - dl2 / 2)
    b2 = fun_angle(s - (l2 - dl2 / 2))

    dl = (dx ** 2 + dy ** 2) ** 0.5
    f1 = g_tie * dl1 / (np.sin(a1) + np.cos(a1) * np.tan(b1))
    f2 = g_tie * dl2 / (np.sin(a2) + np.cos(a2) * np.tan(b2))

    nx2 = nx - f1 * np.cos(a1) + f2 * np.cos(a2)
    ny2 = ny + f1 * np.sin(a1) + f2 * np.sin(a2) + g_arch * dl

    x3 = (dx / 2 * (ny / nx + ny2 / nx2) - dy)
    return x3, nx2, ny2, dl1, dl2
