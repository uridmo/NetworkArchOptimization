import numpy as np


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

    def adapt_doc(self):

        return

    def get_effects(self, name, key=''):
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

        if key:
            if key in effects:
                return effects[key]
            else:
                return self.get_effects('0')['Normal Force']
        else:
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
            if effects['Normal Force'].ndim == 2:
                range_new = effects
            else:
                range_new = range_from_effect(effects)
        if name:
            self.set_effects(range_new, name)
        return range_new

    def add_key(self, name, key, value):
        effects = self.get_effects(name)
        key_ref = list(effects.keys())[0]
        effects = value * np.ones_like(effects[key_ref])
        self.set_effects(effects, name, key=key)
        return


def connect_inner_lists(effect):
    results = []
    for list_i in effect:
        results.extend(list_i)
    return results


def add_effects(*effects):
    added_dict = {}
    for key in effects[0]:
        added_dict[key] = effects[0][key] + effects[1][key]
        for effect in effects[2:]:
            added_dict[key] += effect[key]
    return added_dict


def multiply_effect(effect_1, factor):
    effect = {}
    for key in effect_1:
        effect[key] = factor * effect_1[key]
    return effect


def range_from_effect(effect):
    range_new = {}
    for key in effect:
        range_new[key] = np.vstack((effect[key], effect[key]))
    return range_new


def merge_ranges(*ranges):
    range_merged = {}
    for key in ranges[0]:
        max_stacked = np.vstack(tuple((range_i[key][0] for range_i in ranges)))
        min_stacked = np.vstack(tuple((range_i[key][1] for range_i in ranges)))
        range_merged[key] = np.zeros_like(ranges[0][key])
        range_merged[key][0] = np.max(max_stacked, axis=0)
        range_merged[key][1] = np.min(min_stacked, axis=0)
    return range_merged


def add_ranges(*ranges):
    range_added = add_effects(*ranges)
    return range_added
