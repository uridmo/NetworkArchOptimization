import numpy as np


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
