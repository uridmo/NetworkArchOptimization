class Region:
    def __init__(self):
        self.max_effects = {}
        self.min_effects = {}
        self.degree_of_compliance = {}
        self.normal_force_resistance = None
        self.moment_z_resistance = None
        self.moment_y_resistance = None
        return

    def assign_extrema(self, effects, name, eff):
        if name not in self.max_effects:
            self.max_effects[name] = {}
            self.min_effects[name] = {}
        if eff not in self.max_effects[name]:
            self.max_effects[name][eff] = 0
            self.min_effects[name][eff] = 0

        self.max_effects[name][eff] = max(self.max_effects[name][eff], effects)
        self.min_effects[name][eff] = min(self.min_effects[name][eff], effects)
        return

    def degree_of_compliance(self, name):
        n_max = self.max_effects[name]['Normal Force']
        mz_max = max(self.max_effects[name]['Moment'], -self.min_effects[name]['Moment'])
        my_max = max(self.max_effects[name]['Moment y'], -self.min_effects[name]['Moment y'])
        d_o_c = n_max / self.normal_force_resistance + 8 / 9 * (mz_max / self.moment_z_resistance
                                                                + my_max / self.moment_y_resistance)
        self.degree_of_compliance[name] = d_o_c
        return

    def set_m_y_max(self, name, m_y):
        self.max_effects[name]['Moment y'] = m_y
        self.min_effects[name]['Moment y'] = -m_y
        return
