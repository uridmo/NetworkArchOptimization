from matplotlib import pyplot

from plotting.tables import uls_forces_table, dc_table
from self_equilibrium.embedded_beam import embedded_beam
from self_equilibrium.optimisation import optimize_self_stresses, optimize_self_stresses_tie, \
    optimize_self_stresses_tie_2, optimize_self_stresses_tie_1
from self_equilibrium.static_analysis import zero_displacement, define_by_peak_moment
from structure_elements.arch.circular_arch import CircularArch
from structure_elements.arch.continuous_arch import ContinuousArch
from structure_elements.arch.parabolic_arch import ParabolicArch
from structure_elements.arch.thrust_line_arch import ThrustLineArch
from structure_elements.hangers.constant_change_hangers import ConstantChangeHangerSet
from structure_elements.hangers.hangers import Hangers
from structure_elements.hangers.parallel_hangers import ParallelHangerSet
from structure_elements.hangers.radial_hangers import RadialHangerSet
from structure_elements.networkarch import NetworkArch
from structure_elements.nodes.nodes import Nodes
from structure_elements.tie import Tie


class Bridge:
    def __init__(self, span, rise, n_cross_girders, g_deck, g_wearing, qd_live_load, qc_live_load,
                 arch_shape, arch_optimisation, self_stress_state, self_stress_state_params, cs_arch_x, cs_arch,
                 cs_tie_x, cs_tie, n_hangers, hanger_arrangement, hanger_params, cs_hangers, knuckle,
                 unit_weight_anchorages, unit_price_anchorages):

        self.span = span
        self.rise = rise
        self.cross_girder_amount = n_cross_girders
        self.weight_deck = g_deck
        self.weight_surface_utilities = g_wearing
        self.distributed_live_load = qd_live_load
        self.concentrated_live_load = qc_live_load
        self.self_stress_state = self_stress_state
        self.arch_shape = arch_shape
        self.arch_optimisation = arch_optimisation
        self.arch_cross_sections = cs_arch
        self.arch_cross_sections_x = cs_arch_x
        self.tie_cross_sections = cs_tie
        self.tie_cross_sections_x = cs_tie_x
        self.hangers_amount = n_hangers
        self.hangers_arrangement = hanger_arrangement
        self.hangers_parameters = hanger_params
        self.hangers_cross_section = cs_hangers
        self.unit_weight_anchorages = unit_weight_anchorages
        self.unit_price_anchorages = unit_price_anchorages

        self.ultimate_limit_states = {'Strength-I': 'LL'}

        # Initialize nodes and create hanger set
        nodes = Nodes(accuracy=0.01)

        # Define the first hanger set
        if hanger_arrangement == 'Parallel':
            hanger_set = ParallelHangerSet(nodes, span, n_hangers, *hanger_params)
        elif hanger_arrangement == 'Radial':
            hanger_set = RadialHangerSet(nodes, span, rise, n_hangers, *hanger_params)
        elif hanger_arrangement == 'Constant Change':
            hanger_set = ConstantChangeHangerSet(nodes, span, n_hangers, *hanger_params)
        else:
            raise Exception('Hanger arrangement type "' + hanger_arrangement + '" is not defined')

        # Create the tie and the hangers
        tie = Tie(nodes, span, n_cross_girders, g_deck, g_wearing)
        hangers = Hangers(nodes, hanger_set, span)

        # Define the arch shape (arch shape is optimised later)
        if arch_shape == 'Parabolic':
            arch = ParabolicArch(nodes, span, rise)
        elif arch_shape == 'Circular':
            arch = CircularArch(nodes, span, rise)
        elif arch_shape == 'Continuous optimisation':
            arch = ContinuousArch(nodes, hanger_set, span, rise)
        else:
            raise Exception('Arch shape "' + arch_shape + '" is not defined.')

        # Connect the hangers to the tie and the arch
        tie.assign_hangers(hangers)
        arch.arch_connection_nodes(nodes, hangers)

        # Define cross-sections
        arch.define_cross_sections(nodes, cs_arch_x, cs_arch)
        tie.define_cross_sections(nodes, cs_tie_x, cs_tie)
        hangers.assign_cross_section(cs_hangers)

        # Determine the self equilibrium stress-state
        if self_stress_state == 'Zero-displacement':
            mz_0 = zero_displacement(tie, nodes, hangers, *self_stress_state_params[0:1])
            n_0 = define_by_peak_moment(arch, nodes, hangers, mz_0, *self_stress_state_params[1:])

        elif self_stress_state == 'Embedded-beam':
            k_y = self_stress_state_params[0]
            peak_moment = self_stress_state_params[1]
            mz_0 = embedded_beam(tie, nodes, hangers, k_y)
            n_0 = define_by_peak_moment(arch, nodes, hangers, mz_0, peak_moment=peak_moment)

        elif self_stress_state == 'Tie-optimisation':
            peak_moment = self_stress_state_params[0:1]
            mz_0 = optimize_self_stresses_tie_1(tie, nodes, hangers, *self_stress_state_params[1:2])
            n_0 = define_by_peak_moment(arch, nodes, hangers, mz_0, peak_moment=peak_moment)

        elif self_stress_state == 'Overall-optimisation':
            n_0, mz_0 = optimize_self_stresses(arch, tie, nodes, hangers, *self_stress_state_params)

        else:
            raise Exception('Self-stress state "' + self_stress_state + '" is not defined')

        if knuckle:
            knuckles, dn = hangers.define_knuckles(nodes, span, tie, arch, mz_0, *knuckle)
            mz_0 = 0
            n_0 -= dn

        # Optimize the arch shape if specified
        if arch_optimisation:
            g_arch = cs_arch[0].weight  # TODO: non-constant weights
            arch = ThrustLineArch(nodes, span, rise, g_arch, hangers)
            arch.arch_connection_nodes(nodes, hangers)
            arch.define_cross_sections(nodes, cs_arch_x, cs_arch)
            n_0 = define_by_peak_moment(arch, nodes, hangers, mz_0)

        hangers.assign_length_to_cross_section()
        hangers.assign_permanent_effects()
        arch.assign_permanent_effects(nodes, hangers, n_0, -mz_0, plots=False, name='Arch Permanent Moment')
        tie.assign_permanent_effects(nodes, hangers, -n_0, mz_0, plots=False, name='Tie Permanent Moment')

        # Define the entire network arch structure
        network_arch = NetworkArch(arch, tie, hangers)

        # Calculate the load cases
        network_arch.calculate_load_cases(nodes, qd_live_load, qc_live_load)
        network_arch.assign_wind_effects()
        network_arch.calculate_ultimate_limit_states()

        self.nodes = nodes
        self.network_arch = network_arch
        self.cost = 0
        return

    def plot_elements(self, ax=None):
        if not ax:
            fig, ax = pyplot.subplots(1, 1, figsize=(4, 1.5), dpi=240)
        self.network_arch.tie.plot_elements(ax)
        self.network_arch.arch.plot_elements(ax)
        self.network_arch.hangers.plot_elements(ax)
        ax.set_aspect('equal', adjustable='box')
        pyplot.show()
        return fig

    def plot_effects(self, name, key, fig=None, label='', c='black', lw=1.0, ls='-'):
        if not fig:
            fig, axs = pyplot.subplots(2, 2, figsize=(8, 4), dpi=240)
        axs = fig.get_axes()
        self.network_arch.arch.plot_effects(axs[0], name, key, label=label, c=c, lw=lw, ls=ls)
        self.network_arch.tie.plot_effects(axs[1], name, key, label=label, c=c, lw=lw, ls=ls)
        self.network_arch.hangers.plot_effects(axs[2], name, label=label, c=c, lw=lw, ls=ls)
        return fig

    def plot_all_effects(self, name, fig=None, label='', c='black', lw=1.0, ls='-'):
        if not fig:
            fig, axs = pyplot.subplots(2, 3, figsize=(12, 4), dpi=240)
        axs = fig.get_axes()
        self.network_arch.arch.plot_effects(axs[0], name, 'Normal Force', label=label, c=c, lw=lw, ls=ls)
        self.network_arch.tie.plot_effects(axs[1], name, 'Normal Force', label=label, c=c, lw=lw, ls=ls)
        self.network_arch.hangers.plot_effects(axs[2], name, label=label, c=c, lw=lw, ls=ls)
        self.network_arch.arch.plot_effects(axs[3], name, 'Moment', label=label, c=c, lw=lw, ls=ls)
        self.network_arch.tie.plot_effects(axs[4], name, 'Moment', label=label, c=c, lw=lw, ls=ls)

        return fig

    def internal_forces_table(self, slice_arch, slice_tie, folder, name, all_uls=False):
        cross_sections = self.arch_cross_sections[slice_arch] + self.tie_cross_sections[slice_tie]\
                         + [self.hangers_cross_section]
        uls_forces_table(folder, name, cross_sections, all_uls=all_uls)
        return

    def dc_ratio_table(self, slice_arch, slice_tie, folder, name, uls_types=""):
        cross_sections = self.arch_cross_sections[slice_arch] + self.tie_cross_sections[slice_tie]\
                         + [self.hangers_cross_section]
        dc_table(folder, name, cross_sections, uls_types=uls_types)
        return

    def cost_function(self, slice_arch, slice_tie, table=False):
        costs = []
        for cross_section in self.arch_cross_sections[slice_arch] + self.tie_cross_sections[slice_tie]\
                             + [self.hangers_cross_section]:
            costs.append(cross_section.calculate_cost())

        hanger_cs = self.hangers_cross_section
        weight_anchorages = 2 * self.hangers_amount * self.unit_weight_anchorages
        cost_anchorages = weight_anchorages * self.unit_price_anchorages * hanger_cs.dc_max / hanger_cs.dc_ref
        costs.append(cost_anchorages)
        cost = sum(costs) + 50000
        self.cost = cost
        return cost
