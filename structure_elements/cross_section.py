from math import inf

import numpy as np


class CrossSection:
    def __init__(self, name, g, stiffness, resistance, wind_effects,
                 unit_cost=0, unit_weight=0, dc_ref=0, tie_fractures=(),
                 released=False, fatigue_resistance=1):
        self.name = name
        self.weight = g
        self.stiffness = stiffness
        self.released = released

        self.unit_cost = unit_cost
        self.unit_weight = unit_weight
        self.dc_ref = dc_ref
        self.dc_max = 0
        self.length = 0
        self.cost = 0

        self.effects = {}
        self.degree_of_compliance = {}

        self.normal_force_resistance = resistance[0]
        self.moment_z_resistance = resistance[1]
        self.moment_y_resistance = resistance[2]
        self.fatigue_resistance = fatigue_resistance

        self.wind_effects = None
        self.assign_wind_effects(wind_effects, resistance)

        self.tie_fractures = tie_fractures
        return

    def __repr__(self):
        return self.name

    def get_beam(self):
        beam = list(self.stiffness)
        return beam

    def get_self_weight(self, i):
        load = [i, 0, 0, 0, -self.weight, 0, 0, -self.weight, 0]
        return load

    def append_releases(self, releases, i):
        if self.released:
            releases.append([i, 1, 1])
        return

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
                if name == 'Tie Fracture':
                    stresses = [0]
                    for fracture in self.tie_fractures:
                        frac_name = fracture.name
                        stresses.append(self.effects[name][frac_name+'_top'][2])
                        stresses.append(self.effects[name][frac_name+'_bot'][2])
                    self.degree_of_compliance[name] = max(stresses)/(485000 * 1.15)
                else:
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
            if name == 'Fatigue':
                n_max = self.effects[name]['Normal Force'][0]
                n_min = self.effects[name]['Normal Force'][1]
                d_n = n_max - n_min
                self.effects[name]['Normal Force'][2] = d_n
                self.effects[name]['Normal Force'][3] = d_n
                n_rd = self.fatigue_resistance
                d_o_c = d_n / n_rd
            else:
                n_max = self.effects[name]['Normal Force'][2]
                n_rd = self.normal_force_resistance
                if name == 'Cable_Loss':
                    n_rd = 0.9/0.65 * n_rd
                if name == 'Cable_Replacement':
                    n_rd = 0.8/0.65 * n_rd
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
            dc_1[0] += wind_effects['Normal Force'][0] / resistance[0]
            dc_1[1] += wind_effects['Normal Force'][-1] / resistance[0]
            dc_2[0] += wind_effects['Normal Force'][0] / resistance[0]
            dc_2[1] += wind_effects['Normal Force'][-1] / resistance[0]
        if 'Moment' in wind_effects:
            dc_1[0] += 8 / 9 * wind_effects['Moment'][0] / resistance[1]
            dc_1[1] += 8 / 9 * wind_effects['Moment'][-1] / resistance[1]
            dc_2[0] -= 8 / 9 * wind_effects['Moment'][0] / resistance[1]
            dc_2[1] -= 8 / 9 * wind_effects['Moment'][-1] / resistance[1]
        if 'Moment y' in wind_effects:
            dc_1[0] += 8 / 9 * wind_effects['Moment y'][0] / resistance[2]
            dc_1[1] -= 8 / 9 * wind_effects['Moment y'][0] / resistance[2]
            dc_2[0] += 8 / 9 * wind_effects['Moment y'][0] / resistance[2]
            dc_2[1] -= 8 / 9 * wind_effects['Moment y'][0] / resistance[2]
        wind_effects['D/C_1'] = dc_1
        wind_effects['D/C_2'] = dc_2
        self.wind_effects = wind_effects
        return


class TieFracture:
    def __init__(self, name, a, i_yz, yz_lost, a_lost, i_yz_lost, yz_top, yz_bot):
        self.name = name
        z_new = -a_lost / (a - a_lost) * yz_lost[1]
        y_new = -a_lost / (a - a_lost) * yz_lost[0]
        self.center_of_gravity_z = z_new
        self.center_of_gravity_y = y_new
        self.area = a - a_lost
        self.y_inertia = i_yz[0] - i_yz_lost[0] - (a - a_lost) * z_new ** 2 - a_lost * yz_lost[1] ** 2
        self.z_inertia = i_yz[1] - i_yz_lost[1] - (a - a_lost) * y_new ** 2 - a_lost * yz_lost[0] ** 2
        self.y_top = yz_top[0]
        self.z_top = yz_top[1]
        self.y_bot = yz_bot[0]
        self.z_bot = yz_bot[1]
        return

    def __repr__(self):
        return self.name

    def calculate_stress(self, effects, mask):
        a = self.area
        i_y = self.y_inertia
        i_z = self.z_inertia
        z_c = self.center_of_gravity_z
        y_c = self.center_of_gravity_y

        y_top = self.y_top
        z_top = self.z_top
        y_bot = self.y_bot
        z_bot = self.z_bot

        n = effects['Normal Force'][mask]
        m = effects['Moment'][mask]
        m_y_new = m + n * z_c
        m_z_new = n * y_c
        o_top = n / a + (m_y_new * (z_c - z_top) / i_y) + (m_z_new * (y_c - y_top) / i_z)
        o_bot = n / a + (m_y_new * (z_c - z_bot) / i_y) + (m_z_new * (y_c - y_bot) / i_z)
        return o_top, o_bot
