from bridges.bridge import Bridge
from structure_elements.cross_section import CrossSection


class BlennerhassettBridge(Bridge):
    def __init__(self, span=267.8, rise=53.5, n_cross_girders=13, g_deck=150.4, n_hangers=13, hanger_arrangement='Parallel',
                 hanger_params=tuple([1.0646]), qd_live_load=27, qc_live_load=325, arch_shape='Parabolic',
                 arch_optimisation=False, self_stress_state='Overall-optimisation', exact_cross_sections=False):

        resistance_arch_1 = [130000, 78708, 79115]
        resistance_arch_2 = [108768, 71458, 63445]
        resistance_arch_3 = [82309, 50017, 42729]
        resistance_tie_1 = [153228, 100810, 76190]
        resistance_tie_2 = [117134, 82766, 56610]
        resistance_tie_3 = [100574, 76175, 45792]
        resistance_hanger = [n_hangers/13*3400, 1, 1]

        stiffness_arch_1 = [77429 * 10 ** 3, 31473 * 10 ** 3]
        stiffness_arch_2 = [65997 * 10 ** 3, 28673 * 10 ** 3]
        stiffness_arch_3 = [61814 * 10 ** 3, 28113 * 10 ** 3]
        stiffness_tie_1 = [77429 * 10 ** 3, 31473 * 10 ** 3]
        stiffness_tie_2 = [65997 * 10 ** 3, 28673 * 10 ** 3]
        stiffness_tie_3 = [61814 * 10 ** 3, 28113 * 10 ** 3]
        stiffness_hanger = [n_hangers/13*643.5 * 10 ** 3, 10 ** 3]

        wind_load_arch_1 = {'Normal Force': [-8175], 'Moment': [668], 'Moment y': [13851]}
        wind_load_arch_2 = {'Normal Force': [-7793], 'Moment': [-670], 'Moment y': [10749]}
        wind_load_arch_3 = {'Normal Force': [-4066], 'Moment': [-533], 'Moment y': [2591]}
        wind_load_arch_4 = {'Normal Force': [-3852], 'Moment': [117], 'Moment y': [111]}
        wind_load_tie_1 = {'Normal Force': [5369], 'Moment': [-2327], 'Moment y': [9653]}
        wind_load_tie_2 = {'Normal Force': [7002], 'Moment': [-1109], 'Moment y': [5880]}
        wind_load_tie_3 = {'Normal Force': [6152], 'Moment': [404], 'Moment y': [434]}
        wind_load_tie_4 = {'Normal Force': [5275], 'Moment': [702], 'Moment y': [788]}

        if exact_cross_sections:
            cs_tie_1 = CrossSection('Tie 1', 26.4, stiffness_tie_1, resistance_tie_1, wind_effects=wind_load_tie_1)
            cs_tie_2 = CrossSection('Tie 2', 26.4, stiffness_tie_2, resistance_tie_2, wind_effects=wind_load_tie_2)
            cs_tie_3 = CrossSection('Tie 3', 26.4, stiffness_tie_3, resistance_tie_3, wind_effects=wind_load_tie_3)
            cs_tie_4 = CrossSection('Tie 4', 26.4, stiffness_tie_3, resistance_tie_3, wind_effects=wind_load_tie_4)

            cs_tie = [cs_tie_1, cs_tie_2, cs_tie_3, cs_tie_4]
            cs_tie_x = [6.2, 34.8, 92.13]

            cs_arch_1 = CrossSection('Arch 1', 29.8, stiffness_arch_1, resistance_arch_1, wind_effects=wind_load_arch_1)
            cs_arch_2 = CrossSection('Arch 2', 29.8, stiffness_arch_2, resistance_arch_2, wind_effects=wind_load_arch_2)
            cs_arch_3 = CrossSection('Arch 3', 29.8, stiffness_arch_3, resistance_arch_3, wind_effects=wind_load_arch_3)
            cs_arch_4 = CrossSection('Arch 4', 29.8, stiffness_arch_3, resistance_arch_3, wind_effects=wind_load_arch_4)

            cs_arch = [cs_arch_1, cs_arch_2, cs_arch_3, cs_arch_4]
            cs_arch_x = [3.8, 28.8, 83.91]

            cs_hangers = CrossSection('Hanger', 0, stiffness_hanger, resistance_hanger)
        else:
            cs_tie = [CrossSection(26.4, 50146 * 10 ** 3, 38821 * 10 ** 3)]
            cs_arch = [CrossSection(29.8, 61814 * 10 ** 3, 28113 * 10 ** 3)]
            cs_hangers = CrossSection(0, 643.5 * 10 ** 3, 10 ** 3)
            cs_tie_x, cs_arch_x = [], []

        cs_tie = cs_tie + cs_tie[-2::-1]
        cs_tie_x = cs_tie_x + [-x for x in cs_tie_x[::-1]]
        cs_arch = cs_arch + cs_arch[-2::-1]
        cs_arch_x = cs_arch_x + [-x for x in cs_arch_x[::-1]]

        super().__init__(span, rise, n_cross_girders, g_deck, qd_live_load, qc_live_load,
                         arch_shape, arch_optimisation, self_stress_state, cs_arch_x, cs_arch, cs_tie_x, cs_tie,
                         n_hangers, hanger_arrangement, hanger_params, cs_hangers)
        return
