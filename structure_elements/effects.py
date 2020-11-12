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
