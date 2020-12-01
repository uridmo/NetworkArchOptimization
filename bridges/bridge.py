from matplotlib import pyplot

from plotting.tables import table_from_cross_sections
from self_equilibrium.embedded_beam import embedded_beam
from self_equilibrium.optimisation import optimize_self_stresses, optimize_self_stresses_tie
from self_equilibrium.static_analysis import zero_displacement, define_by_peak_moment
from structure_elements.arch.circular_arch import CircularArch
from structure_elements.arch.continuous_arch import ContinuousArch
from structure_elements.arch.parabolic_arch import ParabolicArch
from structure_elements.arch.thrust_line_arch import get_arch_thrust_line, ThrustLineArch
from structure_elements.hangers.constant_change_hangers import ConstantChangeHangerSet
from structure_elements.hangers.hangers import Hangers
from structure_elements.hangers.parallel_hangers import ParallelHangerSet
from structure_elements.hangers.radial_hangers import RadialHangerSet
from structure_elements.networkarch import NetworkArch
from structure_elements.nodes.nodes import Nodes
from structure_elements.tie import Tie


class Bridge:
    def __init__(self, span, rise, n_cross_girders, g_deck, qd_live_load, qc_live_load,
                 arch_shape, arch_optimisation, self_stress_state, cs_arch_x, cs_arch, cs_tie_x, cs_tie,
                 n_hangers, hanger_arrangement, hanger_params, cs_hangers):

        self.span = span
        self.rise = rise
        self.cross_girder_amount = n_cross_girders
        self.weight_deck = g_deck
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

        self.ultimate_limit_states = {'Strength-I': 'LL'}

        # Initialize nodes and create hanger set
        nodes = Nodes(accuracy=0.001)

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
        tie = Tie(nodes, span, n_cross_girders, g_deck)
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
        hangers.define_cross_section(cs_hangers)

        # Determine the self equilibrium stress-state
        if self_stress_state == 'Zero-displacement':
            mz_0 = zero_displacement(tie, nodes, hangers, dof_rz=True)
            n_0 = define_by_peak_moment(arch, nodes, hangers, mz_0, peak_moment=-5 * 10 ** 3)

        elif self_stress_state == 'Embedded-beam':
            mz_0 = embedded_beam(tie, nodes, hangers, cs_hangers.stiffness[0])
            n_0 = define_by_peak_moment(arch, nodes, hangers, mz_0, peak_moment=-5 * 10 ** 3)

        elif self_stress_state == 'Tie-optimisation':
            mz_0 = optimize_self_stresses_tie(tie, nodes, hangers)
            n_0 = define_by_peak_moment(arch, nodes, hangers, mz_0, peak_moment=-5 * 10 ** 3)

        elif self_stress_state == 'Overall-optimisation':
            n_0, mz_0 = optimize_self_stresses(arch, tie, nodes, hangers)

        else:
            raise Exception('Self-stress state "' + self_stress_state + '" is not defined')

        # Optimize the arch shape if specified
        if arch_optimisation:
            g_arch = cs_arch[0].weight  # TODO: non-constant weights
            arch = ThrustLineArch(nodes, span, rise, g_arch, hangers)
            arch.arch_connection_nodes(nodes, hangers)
            arch.define_cross_sections(nodes, cs_arch_x, cs_arch)
            n_0 = define_by_peak_moment(arch, nodes, hangers, mz_0)

        hangers.assign_permanent_effects()
        arch.assign_permanent_effects(nodes, hangers, n_0, -mz_0, plots=False, name='Arch Permanent Moment')
        tie.assign_permanent_effects(nodes, hangers, -n_0, mz_0, plots=False, name='Tie Permanent Moment')

        # Define the entire network arch structure
        network_arch = NetworkArch(arch, tie, hangers)

        # Calculate the load cases
        network_arch.calculate_dead_load(nodes)
        network_arch.calculate_live_load(nodes, qd_live_load, qc_live_load)
        network_arch.assign_wind_effects()
        network_arch.calculate_ultimate_limit_states()
        network_arch.assign_range_to_sections(['Strength-I', 'Strength-III'])

        self.nodes = nodes
        self.network_arch = network_arch
        return

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

    def cross_section_table(self, slice_arch, slice_tie, folder, name):
        cross_sections = self.arch_cross_sections[slice_arch] + self.tie_cross_sections[slice_tie]
        table_from_cross_sections(folder, name, cross_sections)
        return
