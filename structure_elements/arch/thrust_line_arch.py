import numpy as np
from scipy.optimize import fsolve

from .arch import Arch


class ThrustLineArch(Arch):
    def __init__(self, nodes, span, rise, g_arch, hanger_sets, n=30):
        super().__init__(span, rise)
        x, y = get_arch_thrust_line(span, rise, g_arch, hanger_sets)
        x_arch = [span - i for i in x[-1:0:-1]] + x
        y_arch = y[-1:0:-1]+y

        for i in range(len(x_arch)):
            node = nodes.add_node(x_arch[i], y_arch[i])
            self.nodes.append(node)
        return


def get_arch_thrust_line(span, rise, g_arch, hanger_sets):
    hangers = []
    for hanger in hanger_sets:
        hangers.append(hanger)
    n = fsolve(lambda n: thrust_line_by_n(span, rise, hangers, g_arch, n)[0], 50000)
    x0, x, y = thrust_line_by_n(span, rise, hangers, g_arch, n)
    return x, y


def thrust_line_by_n(span, rise, hangers, g_arch, n):
    x_arch = span / 2
    y_arch = rise
    x = [x_arch]
    y = [y_arch]
    h = float(n)
    dy = 0
    dl = 1
    relevant_hangers = []
    v = 0
    for i, hanger in enumerate(hangers):
        a_i, dx_i = intersect_hanger_with_parabola(y_arch, x_arch, dl, g_arch, v, h, hanger)
        if (dx_i[0] > 0 and a_i[0] > 0) or (dx_i[1] > 0 and a_i[1] > 0):
            relevant_hangers.append(hanger)

    while x_arch < span:
        h_h = []
        dx = []
        a = []
        for hanger in relevant_hangers:
            a_i, dx_i = intersect_hanger_with_parabola(y_arch, x_arch, dl, g_arch, v, h, hanger)
            a.extend(a_i)
            dx.extend(dx_i)
            h_h.extend([hanger, hanger])
        i_min = 1
        val_min = 1.5
        for i, val in enumerate(dx):
            if val > 0:
                if val < val_min:
                    val_min = val
                    i_min = i
        if val_min < 1.5:
            hanger = h_h[i_min]
            x_arch += dx[i_min]
            y_arch = a[i_min]
            v += dx[i_min]*dl * g_arch + np.sin(hanger.inclination)*hanger.prestressing_force
            h -= np.cos(hanger.inclination)*hanger.prestressing_force
            relevant_hangers.remove(hanger)
        else:
            dx = min(1, span-x_arch)
            x_arch += dx
            y_arch -= dx*dy + g_arch/2/h*dl*dx**2
            v += dx*dl*g_arch
        x.append(x_arch)
        y.append(y_arch)
        dy = v/h
        dl = (v**2 + h**2)**0.5/h
    y_end = y[-1]
    return y_end, x, y


def intersect_hanger_with_parabola(y_arch, x_arch, dl, g, v, h, hanger):
    tan_a = np.tan(hanger.inclination)
    x_tie = hanger.tie_node.x

    constant = ((v**2) + (h**2)*(tan_a**2) + 2*h*tan_a*v + 2*dl*g*h*y_arch - 2*dl*g*h*tan_a*x_arch + 2*dl*g*h*tan_a*x_tie)**(1/2)
    dx_1 = -(v + h * tan_a + constant) / (dl * g)
    dx_2 = -(v + h * tan_a - constant) / (dl * g)

    a_1 = -(tan_a * (v + h * tan_a + constant - dl * g * x_arch + dl * g * x_tie)) / (dl * g)
    a_2 = -(tan_a * (v + h * tan_a - constant - dl * g * x_arch + dl * g * x_tie)) / (dl * g)
    a = [a_1, a_2]
    dx = [dx_1, dx_2]
    return a, dx
