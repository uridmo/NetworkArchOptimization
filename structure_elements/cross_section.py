import numpy as np


class CrossSection:
    def __init__(self, g, ea, ei, name='', ga=0, n_rd=0, mz_rd=0, my_rd=0):
        self.name = name

        self.weight = g
        self.axial_stiffness = ea
        self.bending_stiffness = ei
        self.shear_stiffness = ga

        self.max_effects = {}
        self.min_effects = {}
        self.degree_of_compliance = {}
        self.normal_force_resistance = n_rd
        self.moment_z_resistance = mz_rd
        self.moment_y_resistance = my_rd
        return

    def get_beam(self):
        if self.shear_stiffness:
            beam = [self.axial_stiffness, self.bending_stiffness, self.shear_stiffness]
        else:
            beam = [self.axial_stiffness, self.bending_stiffness]
        return beam

    def get_self_weight(self, i):
        load = [i, 0, 0, 0, -self.weight, 0, 0, -self.weight, 0]
        return load

    def degree_of_compliance(self, name):
        n_max = self.max_effects[name]['Normal Force']
        mz_max = max(self.max_effects[name]['Moment'], -self.min_effects[name]['Moment'])
        my_max = max(self.max_effects[name]['Moment y'], -self.min_effects[name]['Moment y'])
        d_o_c = n_max / self.normal_force_resistance + 8 / 9 * (mz_max / self.moment_z_resistance
                                                                + my_max / self.moment_y_resistance)
        self.degree_of_compliance[name] = d_o_c
        return

    def assign_extrema(self, effects, name, key):
        if name not in self.max_effects:
            self.max_effects[name] = {}
            self.min_effects[name] = {}
        if key not in self.max_effects[name]:
            self.max_effects[name][key] = 0
            self.min_effects[name][key] = 0

        self.max_effects[name][key] = max(self.max_effects[name][key], np.max(effects))
        self.min_effects[name][key] = min(self.min_effects[name][key], np.min(effects))
        return

    def set_m_y_max(self, name, m_y):
        self.max_effects[name]['Moment y'] = m_y
        self.min_effects[name]['Moment y'] = -m_y
        return
