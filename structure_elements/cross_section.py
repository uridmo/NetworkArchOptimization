import numpy as np
from math import inf


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

        self.normal_force_resistance = resistance[0]
        self.moment_z_resistance = resistance[1]
        self.moment_y_resistance = resistance[2]

        self.wind_effects = None
        self.assign_wind_effects(wind_effects, resistance)
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
            self.effects[name][key] = [-inf, inf, 0, 0]
        e_max = max(self.effects[name][key][0], np.max(effects))
        e_min = min(self.effects[name][key][1], np.min(effects))
        e_amax = max(e_max, -e_min)
        self.effects[name][key][0] = e_max
        self.effects[name][key][1] = e_min
        self.effects[name][key][2] = e_amax
        self.effects[name][key][3] = e_max if e_max > -e_min else e_min
        return

    def calculate_doc_max(self, name, is_hanger=False, exact_maximum=True):
        if not is_hanger:
            if exact_maximum:
                self.degree_of_compliance[name] = max(self.effects[name]['D/C_1'][2], self.effects[name]['D/C_2'][2])
            else:
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
        weight = 2 * self.length * self.unit_weight
        self.dc_max = self.max_doc()
        self.cost = weight * self.unit_cost * self.dc_max / self.dc_ref
        return self.cost

    def assign_wind_effects(self, wind_effects, resistance):
        dc_1 = [0, 0]
        dc_2 = [0, 0]
        if 'Normal Force' in wind_effects:
            dc_1[0] += wind_effects['Normal Force'][0]/resistance[0]
            dc_1[1] += wind_effects['Normal Force'][-1]/resistance[0]
            dc_2[0] += wind_effects['Normal Force'][0]/resistance[0]
            dc_2[1] += wind_effects['Normal Force'][-1]/resistance[0]
        if 'Moment' in wind_effects:
            dc_1[0] += 8/9 * wind_effects['Moment'][0]/resistance[1]
            dc_1[1] += 8/9 * wind_effects['Moment'][-1]/resistance[1]
            dc_2[0] -= 8/9 * wind_effects['Moment'][0]/resistance[1]
            dc_2[1] -= 8/9 * wind_effects['Moment'][-1]/resistance[1]
        if 'Moment y' in wind_effects:
            dc_1[0] += 8/9 * wind_effects['Moment y'][0]/resistance[2]
            dc_1[1] -= 8/9 * wind_effects['Moment y'][0]/resistance[2]
            dc_2[0] += 8/9 * wind_effects['Moment y'][0]/resistance[2]
            dc_2[1] -= 8/9 * wind_effects['Moment y'][0]/resistance[2]
        wind_effects['D/C_1'] = dc_1
        wind_effects['D/C_2'] = dc_2
        self.wind_effects = wind_effects
        return
