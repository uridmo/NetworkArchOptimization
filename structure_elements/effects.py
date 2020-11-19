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
        effects_key = (effect[key] for effect in effects)
        added_dict[key] = list(map(add_multiple_lists, *effects_key))
    return added_dict


def multiply_effect(effect_1, factor):
    if 'Min' in effect_1:
        effect = {}
        effect['Max'] = multiply_effect(effect_1['Max'], factor)
        effect['Min'] = multiply_effect(effect_1['Min'], factor)
    else:
        effect = {}
        for key in effect_1:
            effect[key] = []
            for i in range(len(effect_1[key])):
                effect[key].append(list(map(lambda x: factor*x, effect_1[key][i])))
    return effect


def get_minmax_effect(*effects):
    effect_max = {}
    effect_min = {}
    for key in effects[0]:
        effects_key = (effect[key] for effect in effects)
        effect_max[key] = list(map(max_multiple_lists, *effects_key))
        effect_min[key] = list(map(min_multiple_lists, *effects_key))
    return effect_max, effect_min


def range_from_effect(effect):
    # effect_max = deepcopy(effect)
    # effect_min = deepcopy(effect)
    range_new = {'Max': effect, 'Min': effect}
    return range_new


def merge_ranges(*ranges):
    range_merged = {'Max': {}, 'Min': {}}
    for key in ranges[0]['Max']:
        effects_max = (r['Max'][key] for r in ranges)
        effects_min = (r['Min'][key] for r in ranges)
        range_merged['Max'][key] = list(map(max_multiple_lists, *effects_max))
        range_merged['Min'][key] = list(map(min_multiple_lists, *effects_min))
    return range_merged


def add_ranges(*ranges):
    range_added = {'Max': {}, 'Min': {}}
    for key in ranges[0]['Max']:
        effects_max = (r['Max'][key] for r in ranges)
        effects_min = (r['Min'][key] for r in ranges)
        range_added['Max'][key] = list(map(add_multiple_lists, *effects_max))
        range_added['Min'][key] = list(map(add_multiple_lists, *effects_min))
    return range_added
