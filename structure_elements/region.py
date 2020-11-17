class Region:
    def __init__(self):
        self.max_effects = {}
        self.min_effects = {}
        return

    def assign_extrema(self, effects, key, eff):
        if key not in self.max_effects:
            self.max_effects[key] = {}
            self.min_effects[key] = {}
        if eff not in self.max_effects[key]:
            self.max_effects[key][eff] = 0
            self.min_effects[key][eff] = 0

        self.max_effects[key][eff] = max(self.max_effects[key][eff], max(effects))
        self.min_effects[key][eff] = min(self.min_effects[key][eff], min(effects))
        return
