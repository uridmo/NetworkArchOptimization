import numpy as np


class CrossSection:
    def __init__(self, name, g, stiffness, resistance, wind_effects={}):
        self.name = name
        self.weight = g
        self.stiffness = stiffness

        self.effects = {}
        self.degree_of_compliance = {}
        self.wind_effects = wind_effects

        self.normal_force_resistance = resistance[0]
        self.moment_z_resistance = resistance[1]
        self.moment_y_resistance = resistance[2]
        return

    def __repr__(self):
        return self.name

    def get_beam(self):
        beam = list(self.stiffness)
        return beam

    def get_self_weight(self, i):
        load = [i, 0, 0, 0, -self.weight, 0, 0, -self.weight, 0]
        return load

    def calculate_doc(self, name):
        n_max = self.effects[name]['Normal Force'][2]
        mz_max = self.effects[name]['Moment'][2]
        my_max = self.effects[name]['Moment y'][2]
        n_rd = self.normal_force_resistance
        mz_rd = self.moment_z_resistance
        my_rd = self.moment_y_resistance
        d_o_c = n_max / n_rd + 8 / 9 * (mz_max / mz_rd + my_max / my_rd)
        self.degree_of_compliance[name] = d_o_c
        return

    def assign_extrema(self, effects, name, key):
        if name not in self.effects:
            self.effects[name] = {}
            self.effects[name] = {}
        if key not in self.effects[name]:
            self.effects[name][key] = [0, 0, 0, 0]
        e_max = max(self.effects[name][key][0], np.max(effects))
        e_min = min(self.effects[name][key][1], np.min(effects))
        e_amax = max(e_max, -e_min)
        self.effects[name][key][0] = e_max
        self.effects[name][key][1] = e_min
        self.effects[name][key][2] = e_amax
        self.effects[name][key][3] = e_max if e_max > -e_min else e_min
        return

    def set_m_y_max(self, name, m_y):
        self.effects[name]['Moment y'] = m_y
        self.effects[name]['Moment y'] = -m_y
        return
