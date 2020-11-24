from bridges.bridge import Bridge
from structure_elements.cross_section import CrossSection


class BlennerhassettBridge(Bridge):
    def __init__(self, span=267.8, rise=53.5, n_cross_girders=13, g_deck=150.4, n_hangers=13, arrangement='Parallel',
                 hanger_params=tuple([1.0646]), qd_live_load=27, qc_live_load=325, arch_shape='Parabolic',
                 exact_cross_sections=False, regions_arch=None, regions_tie=None,
                 strength_combination='0.9 DL/1.35 DL, LL', cable_loss_combination=None):

        if exact_cross_sections:
            cs_tie_1 = CrossSection(26.4, 62441 * 10 ** 3, 46255 * 10 ** 3, name="Tie 1")
            cs_tie_2 = CrossSection(26.4, 53736 * 10 ** 3, 42811 * 10 ** 3, name="Tie 2")
            cs_tie = [cs_tie_1, cs_tie_2, cs_tie_1]
            cs_arch_1 = CrossSection(29.8, 77429 * 10 ** 3, 31473 * 10 ** 3, name="Arch 1",
                                     wind_effects={'Normal Force': [200, -100], 'Moment y': [200, -200]})
            cs_arch_2 = CrossSection(29.8, 65997 * 10 ** 3, 28673 * 10 ** 3, name="Arch 2")
            cs_arch_3 = CrossSection(29.8, 61814 * 10 ** 3, 28113 * 10 ** 3, name="Arch 3")
            cs_arch = [cs_arch_1, cs_arch_2, cs_arch_3, cs_arch_2, cs_arch_1]
            cs_hangers = CrossSection(0, 643.5 * 10 ** 3, 10 ** 3)
            cs_tie_x = [34.8, -34.8]
            cs_arch_x = [3.8, 28.8, -28.8, -3.8]
        else:
            cs_tie = [CrossSection(26.4, 50146 * 10 ** 3, 38821 * 10 ** 3)]
            cs_arch = [CrossSection(29.8, 61814 * 10 ** 3, 28113 * 10 ** 3)]
            cs_hangers = CrossSection(0, 643.5 * 10 ** 3, 10 ** 3)
            cs_tie_x, cs_arch_x = [], []



        super().__init__(span, rise, n_cross_girders, g_deck, qd_live_load, qc_live_load,
                         arch_shape, cs_arch_x, cs_arch, cs_tie_x, cs_tie,
                         n_hangers, arrangement, hanger_params, cs_hangers,
                         strength_combination, cable_loss_combination)
        return
