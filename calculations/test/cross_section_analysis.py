import pickle

import numpy as np
from matplotlib import pyplot
from scipy.integrate import dblquad
from scipy.optimize import minimize
from plotting.general import colors
from shapely.geometry import Polygon
from matplotlib.patches import Rectangle as Rectangle_plot


class CrossSection:
    def __init__(self):
        self.rectangles = []
        return

    def add_rectangle(self, x, y, l, h):
        rectangle = Rectangle(x, y, l, h)
        self.rectangles.append(rectangle)
        return

    def cross_section_properties(self):
        a = 0
        x_c = 0
        y_c = 0
        for rectangle in self.rectangles:
            a_add = rectangle.l*rectangle.h
            x_c = (a*x_c + a_add*(rectangle.x+rectangle.l/2))/(a+a_add)
            y_c = (a*y_c + a_add*(rectangle.y+rectangle.h/2))/(a+a_add)
            a += a_add
        i_y = 0
        i_x = 0
        for rectangle in self.rectangles:
            a_rec = rectangle.l*rectangle.h
            i_x_rec = rectangle.l*rectangle.h**3/12
            i_y_rec = rectangle.l**3*rectangle.h/12
            i_y += (rectangle.x+rectangle.l/2-x_c)**2*a_rec + i_y_rec
            i_x += (rectangle.y+rectangle.h/2-y_c)**2*a_rec + i_x_rec
        return x_c, y_c, a, i_x, i_y

    def elastic_stress(self, N, M_x, M_y, x_m, y_m, x_p, y_p):
        x_c, y_c, a, i_x, i_y = self.cross_section_properties()
        o= N/a + (M_x + N * (y_m-y_c))*(y_p-y_c)/i_y
        return o

    def integrate_stresses(self, stress_function, e, chi_x, chi_y):
        strain_function = lambda x, y: e + chi_x * y + chi_y * x
        stress_function_xy = lambda x, y: stress_function(strain_function(x, y))
        N = 0
        Mx = 0
        My = 0
        for rectangle in self.rectangles:
            i_f = rectangle.integrate_stresses(stress_function_xy)
            N += i_f[0]
            Mx += i_f[1]
            My += i_f[2]
        return N, Mx, My

    def get_strain_function(self, e, chi_x, chi_y):
        strain_function_xy = lambda x, y: y * float(chi_x) + x * float(chi_y) + e
        return strain_function_xy

    def get_corner_strains(self, e, chi_x, chi_y):
        strain_function_xy = self.get_strain_function(e, chi_x, chi_y)
        corner_strains = []
        for rectangle in self.rectangles:
            corner_strains.extend(rectangle.get_corner_strains(strain_function_xy))
        corner_strains = np.array(corner_strains)
        return corner_strains

    def get_points(self):
        XX = []
        YY = []
        for rectangle in self.rectangles:
            xx, yy = rectangle.get_points()
            XX.extend(xx)
            YY.extend(yy)
        XX = np.array(XX)
        YY = np.array(YY)
        return XX, YY

    def get_linear_strain_matrix(self):
        strain_matrix = []
        for rectangle in self.rectangles:
            strain_matrix.append([1, rectangle.y, rectangle.x])
            strain_matrix.append([1, rectangle.y, rectangle.x + rectangle.l])
            strain_matrix.append([1, rectangle.y + rectangle.h, rectangle.x])
            strain_matrix.append([1, rectangle.y + rectangle.h, rectangle.x + rectangle.l])
        A = np.array(strain_matrix)
        return A

    def plot_cross_section(self, ax):
        for rectangle in self.rectangles:
            rectangle.plot_area(ax)
        return


class Rectangle:
    def __init__(self, x, y, l, h):
        self.x = x
        self.y = y
        self.l = l
        self.h = h
        return

    def integrate_stresses(self, stress_function_xy):
        a = self.x
        b = self.x + self.l
        gfun = lambda x: self.y
        hfun = lambda x: self.y + self.h
        func = stress_function_xy
        N = dblquad(func, a, b, gfun, hfun)[0]

        func = lambda y, x: stress_function_xy(x, y) * y
        M_x = dblquad(func, a, b, gfun, hfun)[0]

        func = lambda y, x: stress_function_xy(x, y) * x
        M_y = dblquad(func, a, b, gfun, hfun)[0]
        return N, M_x, M_y

    def get_corner_strains(self, strain_function_xy):
        corner_strains = []
        corner_strains.append(strain_function_xy(self.x, self.y))
        corner_strains.append(strain_function_xy(self.x + self.l, self.y))
        corner_strains.append(strain_function_xy(self.x, self.y + self.h))
        corner_strains.append(strain_function_xy(self.x + self.l, self.y + self.h))
        return corner_strains

    def get_points(self):
        x = np.linspace(self.x, self.x + self.l, num=int(self.l//0.01+2))
        y = np.linspace(self.y, self.y + self.h, num=int(self.h//0.01+2))
        X = []
        Y = []
        for x_i in x:
            Y.extend(list(y))
            X.extend([x_i]*len(y))
        return X, Y

    def plot_area(self, ax):
        ax.add_patch(Rectangle_plot((self.x, self.y), self.l, self.h))
        return


# Scaling factors for optimisation method to work
factor_e = 10**6
factor_chi = 10**6

E_s = 205 * 10 ** 9
E_sh = 1 * 10 ** 9
f_y = 485 * 10 ** 6
e_y = f_y / E_s
f_y_2 = 585 * 10 ** 6
e_y_2 = f_y_2 / E_s


def stress(strain):
    if strain < -e_y:
        return -f_y - (strain + e_y) * E_sh
    elif strain < e_y:
        return strain * E_s
    else:
        return f_y + (strain - e_y) * E_sh


def stress_2(strain):
    if strain < -e_y_2:
        return -f_y_2 - (strain + e_y_2) * E_sh
    elif strain < e_y_2:
        return strain * E_s
    else:
        return f_y_2 + (strain - e_y_2) * E_sh


def ineq_cons(x, e_max, e_min):
    strains = cs_web.get_corner_strains(x[0] / factor_e, x[1] / factor_chi, x[2] / factor_chi)
    strains_0 = np.concatenate((strains - e_min, -strains + e_max))
    return strains_0


def get_interaction_lines(cs, stress_fun, e_max, e_min, ax, c, label):
    cons = [{"type": "ineq", "fun": lambda x: ineq_cons(x, e_max, e_min)},
            {"type": "eq", "fun": lambda x: cs.integrate_stresses(stress_fun, x[0] / factor_e,
                                                                    x[1] / factor_chi,
                                                                    x[2] / factor_chi)[2]}]
    fun_min_N = lambda x: cs.integrate_stresses(stress_fun, x[0] / factor_e, x[1] / factor_chi, x[2] / factor_chi)[0]
    fun_max_N = lambda x: -1*cs.integrate_stresses(stress_fun, x[0] / factor_e, x[1] / factor_chi, x[2] / factor_chi)[0]
    fun_min_M = lambda x: cs.integrate_stresses(stress_fun, x[0] / factor_e, x[1] / factor_chi, x[2] / factor_chi)[1]
    fun_max_M = lambda x: -1*cs.integrate_stresses(stress_fun, x[0] / factor_e, x[1] / factor_chi, x[2] / factor_chi)[1]

    x_0 = np.array([0.0, 0.0, 0.0])
    sol_min = minimize(fun_min_N, x_0, constraints=cons)
    sol_min_M = fun_min_M(sol_min.x)
    print("N_min: "+str(sol_min.fun))
    sol_max = minimize(fun_max_N, x_0, constraints=cons)
    sol_max_M = fun_min_M(sol_max.x)
    print("N_max: "+str(-sol_max.fun))
    N = np.linspace(sol_min.fun, -sol_max.fun, num=18)
    N = np.concatenate((N, np.array([0])))
    N.sort()
    N_c = N[1:-1]
    cons = lambda NN: [{"type": "ineq", "fun": lambda x: ineq_cons(x, e_max, e_min)},
                      {"type": "eq", "fun": lambda x: cs.integrate_stresses(stress_fun, x[0] / factor_e,
                                                                              x[1] / factor_chi,
                                                                              x[2] / factor_chi)[2]},
                      {"type": "eq", "fun": lambda x: cs.integrate_stresses(stress_fun, x[0] / factor_e,
                                                                              x[1] / factor_chi,
                                                                              x[2] / factor_chi)[0]-NN}]
    sol_max = sol_min
    M_min = [sol_min_M]
    M_max = [sol_min_M]
    for n in N_c:
        print("N = "+str(n))
        sol_min = minimize(fun_min_M, sol_min.x, constraints=cons(n))
        print(sol_min.fun)
        sol_max = minimize(fun_max_M, sol_max.x, constraints=cons(n))
        print(-sol_max.fun)
        M_min.append(sol_min.fun)
        M_max.append(-sol_max.fun)

    M_min.append(sol_max_M)
    M_max.append(sol_max_M)
    M_min = np.array(M_min)
    M_max = np.array(M_max)

    ax.plot(N/10**6, M_min/10**6, c=c, label=label)
    ax.plot(N/10**6, M_max/10**6, c=c)

    N_poly = list(N/10**6) + list(N/10**6)[::-1]
    M_poly = list(M_min/10**6) + list(M_max/10**6)[::-1]
    polygon = Polygon([(N_poly[i], M_poly[i]) for i in range(len(M_poly))])
    return polygon


def analyse_cross_sections(cs, name):
    fig, axs = pyplot.subplots(1, 3, figsize=(12, 4), dpi=240)
    cs.plot_cross_section(axs[0])
    axs[0].set_xlim([-1.2, 1.2])
    axs[0].set_ylim([-1.2, 1.2])
    axs[0].axis('off')
    axs[0].set_title('Cross-section')

    poly_y = get_interaction_lines(cs, stress, e_y, -e_y, axs[1], c=colors[0], label="Linear elastic")
    poly_u = get_interaction_lines(cs, stress, 0.01, -e_y, axs[1], c=colors[1], label="Elastic - perfectly plastic (up to 1% strain)")
    poly_y_2 = get_interaction_lines(cs, stress_2, e_y_2, -e_y_2, axs[1], c=colors[2], label="Linear elastic (up to ultimate stress)")
    axs[1].axhline(0, color='black', lw=0.5)
    axs[1].axvline(0, color='black', lw=0.5)
    axs[1].set_title('Interaction diagram')
    axs[1].set_xlabel('N [MN]')
    axs[1].set_ylabel('M [MNm]')

    axs[2].remove()
    handles, labels = axs[1].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.7, 0.85), frameon=False)

    pyplot.show()
    fig.savefig(name + '.png')

    # f = open(name + '.pckl', 'wb')
    # pickle.dump([poly_y, poly_u, poly_y_2], f)
    # f.close()
    return


cs_web = CrossSection()
cs_web.add_rectangle(-0.657, -1.111, 2 * 0.657, 0.044)
cs_web.add_rectangle(-0.657, -1.067, 0.197, 0.025)
cs_web.add_rectangle(0.46, -1.067, 0.197, 0.025)
cs_web.add_rectangle(-0.6239, -1.042, 0.029, 2.084)
# cs_web.add_rectangle(0.628, -1.042, 0.029, 2.084)
cs_web.add_rectangle(-0.657, 1.042, 0.197, 0.025)
cs_web.add_rectangle(0.46, 1.042, 0.197, 0.025)
cs_web.add_rectangle(-0.657, 1.067, 2 * 0.657, 0.044)
print(cs_web.cross_section_properties())
cs_web.add_rectangle(0.6239-0.029, -1.042, 0.029, 2.084)
print(cs_web.cross_section_properties())

analyse_cross_sections(cs_web, 'web fracture')

cs_flange_top = CrossSection()
cs_flange_top.add_rectangle(-0.657, -1.111, 2 * 0.657, 0.044)
cs_flange_top.add_rectangle(-0.657, -1.067, 0.197, 0.025)
cs_flange_top.add_rectangle(0.46, -1.067, 0.197, 0.025)
cs_flange_top.add_rectangle(-0.657, -1.042, 0.029, 2.084)
cs_flange_top.add_rectangle(0.628, -1.042, 0.029, 2.084)
cs_flange_top.add_rectangle(-0.657, 1.042, 0.197, 0.025)
cs_flange_top.add_rectangle(0.46, 1.042, 0.197, 0.025)
# cs_flange_top.add_rectangle(-0.657, 1.067, 2 * 0.657, 0.044)
analyse_cross_sections(cs_flange_top, 'top fracture')
