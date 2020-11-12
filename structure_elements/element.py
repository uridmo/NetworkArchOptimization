from structure_elements.effects import add_effects, multiply_effect, add_ranges, merge_ranges, \
    range_from_optional_effect, range_from_mandatory_effect


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

    def inclusive_range(self, range_name, name=''):
        if ', ' not in range_name:
            if range_name in self.effects_range:
                return self.effects_range[range_name]
            else:
                return range_from_optional_effect(self.get_effects(range_name))
        else:
            names = range_name.split(', ', 1)
            range_1 = self.inclusive_range(names[0])
            range_2 = self.inclusive_range(names[1])
            range_new = add_ranges(range_1, range_2)
            if name:
                self.effects_range[name] = range_new
            return range_new

    # def exclusive_optional_range(self, range_name, name=''):
    #     if ', ' not in range_name:
    #         if range_name in self.effects_range:
    #             return self.effects_range[range_name]
    #         else:
    #             return range_from_optional_effect(self.get_effects(range_name))
    #     else:
    #         names = range_name.split(', ', 1)
    #         range_1 = self.exclusive_optional_range(names[0])
    #         range_2 = self.exclusive_optional_range(names[1])
    #         range_new = merge_ranges(range_1, range_2)
    #         if name:
    #             self.effects_range[name] = range_new
    #         return range_new

    def exclusive_range(self, range_name, name=''):
        if ', ' not in range_name:
            if range_name in self.effects_range:
                return self.effects_range[range_name]
            else:
                return range_from_mandatory_effect(self.get_effects(range_name))
        else:
            names = range_name.split(', ', 1)
            range_1 = self.exclusive_range(names[0])
            range_2 = self.exclusive_range(names[1])
            range_new = merge_ranges(range_1, range_2)
            if name:
                self.effects_range[name] = range_new
            return range_new
