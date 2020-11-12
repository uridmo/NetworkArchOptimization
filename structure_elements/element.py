from structure_elements.effects import add_effects, multiply_effect


class Element:
    def __init__(self):
        self.effects = {}
        self.effects_range = {}
        return

    def set_effects(self, int_forces, name, key=None):
        if name not in self.effects:
            self.effects[name] = {}
        if key:
            self.effects[name][key] = int_forces
        else:
            self.effects[name] = int_forces
        return

    def get_effects(self, name, key=None):
        # Magic
        if ' + ' in name:
            names = name.split(' + ', 1)
            effects = add_effects(self.get_effects(names[0]), self.get_effects(names[1]))
        elif ' - ' in name:
            names = name.split(' - ', 1)
            effects = add_effects(self.get_effects(names[0]), multiply_effect(self.get_effects(names[1]), -1))
        elif ' ' in name:
            names = name.split(' ', 1)
            factor = float(names[0])
            effects = multiply_effect(self.get_effects(names[1]), factor)
        else:
            effects = self.effects[name]

        if key:
            return effects[key]
        else:
            return effects

    def define_effect_range(self, name):

        effects_range = 1
        self.effects_range[name] = effects_range
        return
