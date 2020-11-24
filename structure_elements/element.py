import numpy as np

from structure_elements.effects import add_effects, multiply_effect, connect_inner_lists
from structure_elements.effects import add_ranges, merge_ranges, range_from_effect


class Element:
    def __init__(self):
        self.effects = {}
        return

    def set_effects(self, effects, name, key=None):
        if not key:
            for key in effects:
                self.set_effects(effects[key], name, key=key)
        else:
            if name not in self.effects:
                self.effects[name] = {}
            if type(effects) is list:
                self.effects[name][key] = np.array(connect_inner_lists(effects))
            else:
                self.effects[name][key] = effects
        return

    def get_effects(self, name):
        name = name.replace(' - ', ' + -1 ')
        if name in self.effects:
            effects = self.effects[name]
        elif ' + ' in name:
            names = name.split(' + ')
            effects = add_effects(*(self.get_effects(name) for name in names))
        elif ' ' in name:
            names = name.split(' ', 1)
            factor = float(names[0])
            effects = multiply_effect(self.get_effects(names[1]), factor)
        else:
            return
        return effects

    def get_range(self, range_name, name=''):
        if ', ' in range_name:
            names = range_name.split(', ')
            range_new = add_ranges(*(self.get_range(name) for name in names))
        elif '/' in range_name:
            names = range_name.split('/')
            range_new = merge_ranges(*(self.get_range(name) for name in names))
        else:
            effects = self.get_effects(range_name)
            if 'Max' in effects:
                range_new = effects
            else:
                range_new = range_from_effect(effects)
        if name:
            self.set_effects(range_new, name)
        return range_new
