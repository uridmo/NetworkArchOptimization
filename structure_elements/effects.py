import numpy as np


def add_multiple(*a_i):
    return sum(a_i)


def add_multiple_lists(*lists):
    added_lists = list(map(add_multiple, *lists))
    return added_lists


def max_multiple_lists(*lists):
    max_lists = list(map(max, *lists))
    return max_lists


def connect_inner_lists(effect):
    results = []
    for list_i in effect:
        results.extend(list_i)
    return results


def min_multiple_lists(*lists):
    min_lists = list(map(min, *lists))
    return min_lists


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


# def get_minmax_effect(*effects):
#     effect_max = effects[0]
#     effect_min = effects[0]
#     for key in effects[0]:
#         for effect in effects[1:]:
#             effect_max[key] = np.maximum(effect_max[key], effect[key])
#             effect_min[key] = np.minimum(effect_max[key], effect[key])
#     return effect_max, effect_min


def range_from_effect(effect):
    range_new = np.vstack((effect, effect))
    return range_new


def merge_ranges(*ranges):
    range_merged = {'Min': {}, 'Max': {}}
    for key in ranges[0]['Min']:
        range_merged['Max'][key] = np.maximum(ranges[0][key][0], ranges[1][key][1])
        range_merged['Min'][key] = np.minimum(ranges[0]['Min'][key], ranges[1]['Min'][key])
        for range_i in ranges[2:]:
            range_merged['Max'][key] = np.maximum(range_merged['Max'][key], range_i['Max'][key])
            range_merged['Min'][key] = np.minimum(range_merged['Min'][key], range_i['Min'][key])
    return range_merged


def add_ranges(*ranges):
    range_added = {'Max': {}, 'Min': {}}
    effects_max = (range_i['Max'] for range_i in ranges)
    effects_min = (range_i['Min'] for range_i in ranges)
    range_added['Max'] = add_effects(*effects_max)
    range_added['Min'] = add_effects(*effects_min)
    return range_added
