import pickle

import numpy as np

from bridges.bridge import Bridge
from structure_elements.cross_section import CrossSection, TieFracture


class BlennerhassettBridge(Bridge):
    def __init__(self, span=267.8, rise=53.5, n_cross_girders=13, g_deck=115.3, g_utilities=35.1, n_hangers=13,
                 hanger_arrangement='Parallel', hanger_params=(1.117,), qd_live_load=23, qc_live_load=1063,
                 arch_shape='Parabolic', arch_optimisation=True, self_stress_state='Tie-optimisation',
                 self_stress_state_params=(), exact_stiffness=True, knuckles=True, x_lost_cable=0.25):

        unit_weight_arch_1 = 2467.05
        unit_weight_arch_2 = 2310.68
        unit_weight_arch_3 = 2310.68
        unit_weight_tie_1 = 2334.10
        unit_weight_tie_2 = 2008.71
        unit_weight_tie_3 = 2008.71

        unit_weight_hanger = 31.9 * 13 / n_hangers
        unit_weight_anchorages = 2322.82 * 13 / n_hangers

        unit_price_arch = 4
        unit_price_tie = 3.5
        unit_price_hanger = 22
        unit_price_anchorages = 9

        # Load the demand / capacity ratios from the base case
        try:
            f = open('../base case/dc_ratios.pckl', 'rb')
            dc = pickle.load(f)
        except FileNotFoundError:
            dc = [1] * 7

        dc_arch_1_ref, dc_arch_2_ref, dc_arch_3_ref = dc[0], dc[1], dc[2]
        dc_tie_1_ref, dc_tie_2_ref, dc_tie_3_ref, dc_hanger_ref = dc[3], dc[4], dc[5], dc[6]

        resistance_arch_1 = [130000, 78708, 79115]
        resistance_arch_2 = [108768, 71458, 63445]
        resistance_arch_3 = [82309, 50017, 42729]
        resistance_tie_1 = [153228, 100810, 76190]
        resistance_tie_2 = [117134, 82766, 56610]
        resistance_tie_3 = [100574, 76175, 45792]
        resistance_hanger = [13 / n_hangers * 4190, 1, 1]

        stiffness_arch_1 = [77429 * 10 ** 3, 31473 * 10 ** 3]
        stiffness_arch_2 = [65997 * 10 ** 3, 28673 * 10 ** 3]
        stiffness_arch_3 = [61814 * 10 ** 3, 28113 * 10 ** 3]
        stiffness_tie_1 = [77429 * 10 ** 3, 31473 * 10 ** 3]
        stiffness_tie_2 = [65997 * 10 ** 3, 28673 * 10 ** 3]
        stiffness_tie_3 = [61814 * 10 ** 3, 28113 * 10 ** 3]
        stiffness_hanger = [13 / n_hangers * 643.5 * 10 ** 3, 10 ** 6]

        wind_load_arch_1 = {'Normal Force': [-8175], 'Moment': [668], 'Moment y': [13851, -13851]}
        wind_load_arch_2 = {'Normal Force': [-7793], 'Moment': [-670], 'Moment y': [10749, -10749]}
        wind_load_arch_3 = {'Normal Force': [-4066], 'Moment': [-533], 'Moment y': [2591, -2591]}
        wind_load_arch_4 = {'Normal Force': [-3852], 'Moment': [117], 'Moment y': [111, -111]}
        wind_load_tie_1 = {'Normal Force': [5369], 'Moment': [-2327], 'Moment y': [9653, -9653]}
        wind_load_tie_2 = {'Normal Force': [7002], 'Moment': [-1109], 'Moment y': [5880, -5880]}
        wind_load_tie_3 = {'Normal Force': [6152], 'Moment': [404], 'Moment y': [434, -434]}
        wind_load_tie_4 = {'Normal Force': [5275], 'Moment': [702], 'Moment y': [788, -788]}
        wind_load_hangers = {'Normal Force': [480]}

        tie_fracture_1_web = TieFracture('Web', 0.369, 0.150, 0, 0.1089, 0.0267, -0.8826, 0.8826)
        tie_fracture_2_web = TieFracture('Web', 0.314, 0.137, 0, 0.0817, 0.0200, -0.8826, 0.8826)
        tie_fracture_3_web = TieFracture('Web', 0.294, 0.134, 0, 0.0762, 0.0187, -0.8826, 0.8826)
        tie_fracture_1_top = TieFracture('Top', 0.369, 0.150, 0.857, 0.0619, 0, -0.8826, 0.8573)
        tie_fracture_2_top = TieFracture('Top', 0.314, 0.137, 0.857, 0.0619, 0, -0.8826, 0.8573)
        tie_fracture_3_top = TieFracture('Top', 0.294, 0.134, 0.857, 0.0619, 0, -0.8826, 0.8573)
        tie_fracture_1_bottom = TieFracture('Bottom', 0.369, 0.150, -0.857, 0.0619, 0, -0.8573, 0.8826)
        tie_fracture_2_bottom = TieFracture('Bottom', 0.314, 0.137, -0.857, 0.0619, 0, -0.8573, 0.8826)
        tie_fracture_3_bottom = TieFracture('Bottom', 0.294, 0.134, -0.857, 0.0619, 0, -0.8573, 0.8826)

        if not exact_stiffness:
            stiffness_tie_1 = stiffness_tie_3
            stiffness_tie_2 = stiffness_tie_3
            stiffness_arch_1 = stiffness_arch_3
            stiffness_arch_2 = stiffness_arch_3
            tie_fracture_1_web = tie_fracture_3_web
            tie_fracture_2_web = tie_fracture_3_web
            tie_fracture_1_top = tie_fracture_3_top
            tie_fracture_2_top = tie_fracture_3_top
            tie_fracture_1_bottom = tie_fracture_3_bottom
            tie_fracture_2_bottom = tie_fracture_3_bottom

        tie_fractures_1 = [tie_fracture_1_web, tie_fracture_1_top, tie_fracture_1_bottom]
        tie_fractures_2 = [tie_fracture_2_web, tie_fracture_2_top, tie_fracture_2_bottom]
        tie_fractures_3 = [tie_fracture_3_web, tie_fracture_3_top, tie_fracture_3_bottom]

        cs_tie_0 = CrossSection('Tie 0', 26.4, stiffness_tie_1, resistance_tie_1, wind_effects=wind_load_tie_1,
                                tie_fractures=tie_fractures_1)
        cs_tie_1 = CrossSection('Tie 1', 26.4, stiffness_tie_2, resistance_tie_2, wind_effects=wind_load_tie_2,
                                unit_cost=unit_price_tie, unit_weight=unit_weight_tie_1, dc_ref=dc_tie_1_ref,
                                tie_fractures=tie_fractures_2)
        cs_tie_2 = CrossSection('Tie 2', 26.4, stiffness_tie_3, resistance_tie_3, wind_effects=wind_load_tie_3,
                                unit_cost=unit_price_tie, unit_weight=unit_weight_tie_2, dc_ref=dc_tie_2_ref,
                                tie_fractures=tie_fractures_3)
        cs_tie_3 = CrossSection('Tie 3', 26.4, stiffness_tie_3, resistance_tie_3, wind_effects=wind_load_tie_4,
                                unit_cost=unit_price_tie, unit_weight=unit_weight_tie_3, dc_ref=dc_tie_3_ref,
                                tie_fractures=tie_fractures_3)

        cs_tie = [cs_tie_0, cs_tie_1, cs_tie_2, cs_tie_3]
        cs_tie_x = [6.2, 34.8, 92.13]

        cs_arch_0 = CrossSection('Arch 0', 29.8, stiffness_arch_1, resistance_arch_1, wind_effects=wind_load_arch_1)
        cs_arch_1 = CrossSection('Arch 1', 29.8, stiffness_arch_2, resistance_arch_2, wind_effects=wind_load_arch_2,
                                 unit_cost=unit_price_arch, unit_weight=unit_weight_arch_1, dc_ref=dc_arch_1_ref)
        cs_arch_2 = CrossSection('Arch 2', 29.8, stiffness_arch_3, resistance_arch_3, wind_effects=wind_load_arch_3,
                                 unit_cost=unit_price_arch, unit_weight=unit_weight_arch_2, dc_ref=dc_arch_2_ref)
        cs_arch_3 = CrossSection('Arch 3', 29.8, stiffness_arch_3, resistance_arch_3, wind_effects=wind_load_arch_4,
                                 unit_cost=unit_price_arch, unit_weight=unit_weight_arch_3, dc_ref=dc_arch_3_ref)

        cs_arch = [cs_arch_0, cs_arch_1, cs_arch_2, cs_arch_3]
        cs_arch_x = [3.8, 28.8, 83.91]

        cs_hangers = CrossSection('Hangers', 0, stiffness_hanger, resistance_hanger, wind_effects=wind_load_hangers,
                                  unit_cost=unit_price_hanger, unit_weight=unit_weight_hanger, dc_ref=dc_hanger_ref)

        # Mirror the cross-sections
        cost_cross_sections = cs_arch[1:] + cs_tie[1:] + [cs_hangers]
        cs_tie = cs_tie + cs_tie[-2::-1]
        cs_tie_x = cs_tie_x + [-x for x in cs_tie_x[::-1]]
        cs_arch = cs_arch + cs_arch[-2::-1]
        cs_arch_x = cs_arch_x + [-x for x in cs_arch_x[::-1]]

        if knuckles:
            cs_knuckle = CrossSection('Knuckle', 0, [28452 * 10 ** 3, 32380 * 10 ** 3], [1, 1, 1])
            knuckle_x = 4.1
            knuckle_inclination = np.radians(110)
            knuckle = (cs_knuckle, knuckle_x, knuckle_inclination)
        else:
            knuckle = ()

        super().__init__(span, rise, n_cross_girders, g_deck, g_utilities, qd_live_load, qc_live_load, arch_shape,
                         arch_optimisation, self_stress_state, self_stress_state_params, cs_arch_x, cs_arch, cs_tie_x,
                         cs_tie, n_hangers, hanger_arrangement, hanger_params, cs_hangers, knuckle,
                         x_lost_cable, cost_cross_sections, unit_weight_anchorages, unit_price_anchorages)
        return
