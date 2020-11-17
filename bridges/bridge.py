class Bridge:
    def __init__(self, span, rise, n_cross_girders, g_deck, qd_live_load, qc_live_load,
                 arch_shape, x_cs_arch, cs_arch, x_reg_arch, reg_arch, x_cs_tie, cs_tie,
                 x_reg_tie, reg_tie, n_hanger, arrangement, hanger_params, cs_hangers,
                 strength_combination, cable_loss_combination):

        self.span = span
        self.rise = rise
        self.cross_girder_amount = n_cross_girders
        self.weight_deck = g_deck
        self.distributed_live_load = qd_live_load
        self.concentrated_live_load = qc_live_load
        self.arch_shape = arch_shape
        self.arch_cross_sections = cs_arch
        self.arch_cross_sections_x = x_cs_arch
        self.arch_regions = reg_arch
        self.arch_regions_x = x_reg_arch
        self.tie_cross_sections = cs_tie
        self.tie_cross_sections_x = x_cs_tie
        self.tie_regions = reg_tie
        self.tie_regions_x = x_reg_tie
        self.hangers_amount = n_hanger
        self.hangers_arrangement = arrangement
        self.hangers_parameters = hanger_params
        self.hangers_cross_section = cs_hangers
        self.strength_combination = strength_combination
        self.cable_loss_combination = cable_loss_combination
        return

    def analyse(self):
        network_arch = self.tie_regions
        return network_arch
