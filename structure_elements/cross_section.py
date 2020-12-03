import numpy as np


class CrossSection:
    def __init__(self, name, g, stiffness, resistance, wind_effects={},
                 unit_cost=0, unit_weight=0, dc_ref=0, load_ref=""):
        self.name = name
        self.weight = g
        self.stiffness = stiffness

        self.unit_cost = unit_cost
        self.unit_weight = unit_weight
        self.dc_ref = dc_ref
        self.dc_max = 0
        self.load_ref = load_ref
        self.length = 0
        self.cost = 0

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

    def calculate_doc(self, name, is_hanger=False):
        if not is_hanger:
            n_max = self.effects[name]['Normal Force'][2]
            mz_max = self.effects[name]['Moment'][2]
            my_max = self.effects[name]['Moment y'][2]
            n_rd = self.normal_force_resistance
            mz_rd = self.moment_z_resistance
            my_rd = self.moment_y_resistance
            d_o_c = n_max / n_rd + 8 / 9 * (mz_max / mz_rd + my_max / my_rd)
            self.degree_of_compliance[name] = d_o_c
        else:
            n_max = self.effects[name]['Normal Force'][2]
            n_rd = self.normal_force_resistance
            d_o_c = n_max / n_rd
            self.degree_of_compliance[name] = d_o_c
        return

    def set_m_y_max(self, name, m_y):
        self.effects[name]['Moment y'] = m_y
        self.effects[name]['Moment y'] = -m_y
        return

    def max_doc(self):
        doc_max = 0.01
        for name in self.degree_of_compliance:
            doc_max = max(doc_max, self.degree_of_compliance[name])
        return doc_max

    def calculate_cost(self):
        self.weight = 2 * self.length * self.unit_weight
        self.dc_max = self.max_doc()
        self.cost = self.weight * self.unit_cost * self.dc_max / self.dc_ref
        return self.cost
