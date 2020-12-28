import numpy as np
from matplotlib import pyplot
from scipy.integrate import dblquad
from scipy.optimize import minimize
from plotting.general import colors
from pylab import meshgrid,cm,imshow,contour,clabel,colorbar,axis,title,show
from matplotlib.patches import Rectangle as Rectangle_plot


class CrossSection:
    def __init__(self):
        self.rectangles = []
        return

    def add_rectangle(self, x, y, l, h):
        rectangle = Rectangle(x, y, l, h)
        self.rectangles.append(rectangle)
        return

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


factor_e = 10**6
factor_chi = 10**6

E_s = 205 * 10 ** 9
E_sh = 1 * 10 ** 9
f_y = 485 * 10 ** 6
e_y = f_y / E_s


def stress(strain):
    if strain < -e_y:
        return -f_y - (strain + e_y) * E_sh
    elif strain < e_y:
        return strain * E_s
    else:
        return f_y + (strain - e_y) * E_sh


f_y_2 = 1.2 * 485 * 10 ** 6
e_y_2 = f_y_2 / E_s


def stress_2(strain):
    if strain < -e_y_2:
        return -f_y_2 - (strain + e_y_2) * E_sh
    elif strain < e_y_2:
        return strain * E_s
    else:
        return f_y_2 + (strain - e_y_2) * E_sh


cs_1 = CrossSection()
cs_1.add_rectangle(-0.657, -1.111, 2*0.657, 0.044)
cs_1.add_rectangle(-0.657, -1.067, 0.197, 0.025)
cs_1.add_rectangle(0.46, -1.067, 0.197, 0.025)
# cs_1.add_rectangle(-0.657, -1.042, 0.029, 2.084)
cs_1.add_rectangle(0.628, -1.042, 0.029, 2.084)
cs_1.add_rectangle(-0.657, 1.042, 0.197, 0.025)
cs_1.add_rectangle(0.46, 1.042, 0.197, 0.025)
cs_1.add_rectangle(-0.657, 1.067, 2*0.657, 0.044)

x_0 = np.array([0.0, 0.0, 0.0])


def ineq_cons(x, e_max, e_min):
    strains = cs_1.get_corner_strains(x[0] / factor_e, x[1] / factor_chi, x[2] / factor_chi)
    strains_0 = np.concatenate((strains - e_min, -strains + e_max))
    return strains_0


def get_interaction_lines(stress_fun, e_max, e_min, ax, c, label):
    cons = [{"type": "ineq", "fun": lambda x: ineq_cons(x, e_max, e_min)},
            {"type": "eq", "fun": lambda x: cs_1.integrate_stresses(stress_fun, x[0] / factor_e,
                                                                    x[1] / factor_chi,
                                                                    x[2] / factor_chi)[2]}]
    fun_min_N = lambda x: cs_1.integrate_stresses(stress_fun, x[0] / factor_e, x[1] / factor_chi, x[2] / factor_chi)[0]
    fun_max_N = lambda x: -1*cs_1.integrate_stresses(stress_fun, x[0] / factor_e, x[1] / factor_chi, x[2] / factor_chi)[0]
    fun_min_M = lambda x: cs_1.integrate_stresses(stress_fun, x[0] / factor_e, x[1] / factor_chi, x[2] / factor_chi)[1]
    fun_max_M = lambda x: -1*cs_1.integrate_stresses(stress_fun, x[0] / factor_e, x[1] / factor_chi, x[2] / factor_chi)[1]

    sol_min = minimize(fun_min_N, x_0, constraints=cons)
    sol_min_M = fun_min_M(sol_min.x)
    print("N_min: "+str(sol_min.fun))
    sol_max = minimize(fun_max_N, x_0, constraints=cons)
    sol_max_M = fun_min_M(sol_max.x)
    print("N_max: "+str(-sol_max.fun))
    N = np.linspace(sol_min.fun, -sol_max.fun, num=30)
    N = np.concatenate((N, np.array([0])))
    N = N.sort()
    N_c = N[1:-1]
    cons = lambda NN: [{"type": "ineq", "fun": lambda x: ineq_cons(x, e_max, e_min)},
                      {"type": "eq", "fun": lambda x: cs_1.integrate_stresses(stress_fun, x[0] / factor_e,
                                                                              x[1] / factor_chi,
                                                                              x[2] / factor_chi)[2]},
                      {"type": "eq", "fun": lambda x: cs_1.integrate_stresses(stress_fun, x[0] / factor_e,
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
    return


fig, axs = pyplot.subplots(1, 1, figsize=(4, 4), dpi=720)
cs_1.plot_cross_section(axs)
axs.set_xlim([-1, 1])
axs.set_ylim([-1.5, 1.5])

fig_2, axs = pyplot.subplots(1, 1, figsize=(4, 4), dpi=720)
get_interaction_lines(stress, e_y, -e_y, axs, c=colors[0], label="Test 1")
get_interaction_lines(stress, 0.01, -e_y, axs, c=colors[1], label="Test 2")
get_interaction_lines(stress_2, e_y_2, -e_y_2, axs, c=colors[2], label="Test 3")
axs.axhline(0, color='black', lw=0.5)
axs.axvline(0, color='black', lw=0.5)

pyplot.show()



# print(cs_1.integrate_stresses(stress, x[0] / factor_e, x[1] / factor_chi, x[2] / factor_chi))
# print(cs_1.get_corner_strains(x[0] / factor_e, x[1] / factor_chi, x[2] / factor_chi))
