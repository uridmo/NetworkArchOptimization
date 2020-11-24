from matplotlib import pyplot

from self_equilibrium.optimisation import optimize_self_stresses
from self_equilibrium.static_analysis import zero_displacement, define_by_peak_moment
from structure_elements.arch.parabolic_arch import ParabolicArch
from structure_elements.hangers.constant_change_hangers import ConstantChangeHangerSet
from structure_elements.hangers.hangers import Hangers
from structure_elements.hangers.parallel_hangers import ParallelHangerSet
from structure_elements.hangers.radial_hangers import RadialHangerSet
from structure_elements.networkarch import NetworkArch
from structure_elements.nodes.nodes import Nodes
from structure_elements.tie import Tie


class Bridge:
    def __init__(self, span, rise, n_cross_girders, g_deck, qd_live_load, qc_live_load,
                 arch_shape, cs_arch_x, cs_arch, cs_tie_x, cs_tie,
                 n_hangers, arrangement, hanger_params, cs_hangers,
                 strength_combination, cable_loss_combination):

        geometry = {'Span': span, 'Rise': rise, 'Arch shape': arch_shape, 'Hanger arrangement': arrangement,
                    'Hanger parameters': hanger_params, 'Amount of cross-girders': n_cross_girders,
                    'Amount of hangers': n_hangers}
        cross_sections = []
        loads = {}
        self.input = {'Span': span, 'Rise': rise, 'Amount of cross-girders': n_cross_girders,
                      'Weight deck': g_deck, 'Distributed live load': qd_live_load,
                      'Concentrated live load': qc_live_load, 'Arch shape': arch_shape, 'Arch cross-sections': cs_arch}
        self.span = span
        self.rise = rise
        self.cross_girder_amount = n_cross_girders
        self.weight_deck = g_deck
        self.distributed_live_load = qd_live_load
        self.concentrated_live_load = qc_live_load
        self.arch_shape = arch_shape
        self.arch_cross_sections = cs_arch
        self.arch_cross_sections_x = cs_arch_x
        self.tie_cross_sections = cs_tie
        self.tie_cross_sections_x = cs_tie_x
        self.hangers_amount = n_hangers
        self.hangers_arrangement = arrangement
        self.hangers_parameters = hanger_params
        self.hangers_cross_section = cs_hangers
        self.strength_combination = strength_combination
        self.cable_loss_combination = cable_loss_combination

        # Initialize nodes and create hanger set
        nodes = Nodes()

        # Define the hanger set
        if arrangement == 'Parallel':
            hanger_set = ParallelHangerSet(nodes, span, n_hangers, *hanger_params)
        elif arrangement == 'Radial':
            hanger_set = RadialHangerSet(nodes, span, rise, n_hangers, *hanger_params)
        elif arrangement == 'Constant Change':
            hanger_set = ConstantChangeHangerSet(nodes, span, n_hangers, *hanger_params)
        else:
            raise Exception('Hanger arrangement type "' + arrangement + '" is not defined')

        # Mirror the hanger set and assign stiffness
        hangers = Hangers(nodes, hanger_set, span)

        # Create the structural elements
        tie = Tie(nodes, span, n_cross_girders, g_deck)
        arch = ParabolicArch(nodes, span, rise)

        # Assign the hangers to the tie
        tie.assign_hangers(hangers)
        arch.arch_connection_nodes(nodes, hangers)

        # Define cross-sections
        arch.define_cross_sections(nodes, cs_arch_x, cs_arch)
        tie.define_cross_sections(nodes, cs_tie_x, cs_tie)
        hangers.define_cross_section(cs_hangers)

        # Determine the self equilibrium stress-state
        i = 1
        if i == 1:
            mz_0 = zero_displacement(tie, nodes, hangers, dof_rz=True)
            n_0 = define_by_peak_moment(arch, nodes, hangers, mz_0, peak_moment=-5 * 10 ** 3)

            hangers.assign_permanent_effects()
            arch.assign_permanent_effects(nodes, hangers, n_0, -mz_0, plots=False, name='Arch Permanent Moment')
            tie.assign_permanent_effects(nodes, hangers, -n_0, mz_0, plots=False, name='Tie Permanent Moment')
        else:

            # blennerhassett_forces(arch, tie, nodes, hangers)
            optimize_self_stresses(arch, tie, nodes, hangers)

        # Define the entire network arch structure
        network_arch = NetworkArch(arch, tie, hangers)

        # Calculate the load cases
        network_arch.calculate_dead_load(nodes)
        network_arch.calculate_live_load(nodes, qd_live_load, qc_live_load)
        network_arch.assign_range_to_sections('LL')


        self.nodes = nodes
        self.network_arch = network_arch
        return

    def analyse(self):
        network_arch = self.tie_regions
        return network_arch

    def plot_elements(self, ax):
        self.network_arch.tie.plot_elements(ax)
        self.network_arch.arch.plot_elements(ax)
        self.network_arch.hangers.plot_elements(ax)
        return

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
