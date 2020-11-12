from copy import deepcopy


def add_effects(effect_1, effect_2):
    effect = deepcopy(effect_1)
    for key in effect_1:
        for i in range(len(effect_1[key])):
            for j in range(len(effect_1[key][i])):
                effect[key][i][j] += effect_2[key][i][j]
    return effect


def multiply_effect(effect_1, factor):
    effect = deepcopy(effect_1)
    for key in effect_1:
        for i in range(len(effect_1[key])):
            for j in range(len(effect_1[key][i])):
                effect[key][i][j] *= factor
    return effect


def get_minmax_effect(effect_1, effect_2):
    effect_max = deepcopy(effect_1)
    effect_min = deepcopy(effect_1)
    for key in effect_1:
        for i in range(len(effect_1[key])):
            for j in range(len(effect_1[key][i])):
                effect_max[key][i][j] = max(effect_1[key][i][j], effect_2[key][i][j])
                effect_min[key][i][j] = min(effect_1[key][i][j], effect_2[key][i][j])
    return effect_max, effect_min


def range_from_mandatory_effect(effect):
    effect_max = deepcopy(effect)
    effect_min = deepcopy(effect)
    range_new = {'Max': effect_max, 'Min': effect_min}
    return range_new


def range_from_optional_effect(effect):
    effect_max = deepcopy(effect)
    effect_min = deepcopy(effect)
    for key in effect_max:
        for i in range(len(effect_max[key])):
            for j in range(len(effect_max[key][i])):
                effect_max[key][i][j] = max(effect[key][i][j], 0)
                effect_min[key][i][j] = min(effect[key][i][j], 0)
    range_new = {'Max': effect_max, 'Min': effect_min}
    return range_new


def merge_ranges(range_1, range_2):
    range_merged = deepcopy(range_1)
    for key in range_2['Max']:
        for i in range(len(range_2['Max'][key])):
            for j in range(len(range_2['Max'][key][i])):
                range_merged['Max'][key][i][j] = max(range_1['Max'][key][i][j], range_2['Max'][key][i][j])
                range_merged['Min'][key][i][j] = min(range_1['Min'][key][i][j], range_2['Min'][key][i][j])
    return range_merged


def add_ranges(range_1, range_2):
    range_added = deepcopy(range_1)
    range_added['Max'] = add_effects(range_1['Max'], range_2['Max'])
    range_added['Min'] = add_effects(range_1['Min'], range_2['Min'])
    return range_added
