from matplotlib import pyplot

from plotting.supports import plot_supports_new
from plotting.tables import uls_forces_table, dc_table, cost_table
from self_equilibrium.embedded_beam import embedded_beam
from self_equilibrium.optimisation import optimize_self_stresses, optimize_self_stresses_tie_1
from structure_elements.arch.circular_arch import CircularArch
from structure_elements.arch.continuous_arch import ContinuousArch
from structure_elements.arch.parabolic_arch import ParabolicArch
from structure_elements.arch.polynomial_arch import QuarticArch
from structure_elements.arch.polynomial_arch_fit import PolynomialArch
from structure_elements.arch.spline_arch_fit import SplineArch
from structure_elements.arch.thrust_line_arch import ThrustLineArch
from structure_elements.hangers.constant_change_hangers import ConstantChangeHangerSet
from structure_elements.hangers.hangers import Hangers
from structure_elements.hangers.parallel_hangers import ParallelHangerSet
from structure_elements.hangers.radial_hangers import RadialHangerSet
from structure_elements.networkarch import NetworkArch
from structure_elements.nodes import Nodes
from structure_elements.tie import Tie


class Bridge:
    def __init__(self, span, rise, n_floor_beams, g_deck, g_utilities, q_ll_d, q_ll_c, qc_fatigue,
                 arch_shape, arch_optimisation, curve_fitting, self_stress_state, self_stress_state_params, cs_arch_x,
                 cs_arch, cs_tie_x, cs_tie, n_hangers, hanger_arrangement, hanger_params, cs_hangers, knuckle,
                 cable_loss_events, cost_cross_sections, unit_weight_anchorages, unit_price_anchorages):

        self.input = {'span': span, 'rise': rise, 'cross_girder_amount': n_floor_beams, 'weight_deck': g_deck,
                      'weight_surface_utilities': g_utilities, 'distributed_live_load': q_ll_d,
                      'concentrated_live_load': q_ll_c, 'self_stress_state': self_stress_state,
                      'arch_shape': arch_shape, 'arch_optimisation': arch_optimisation, 'arch_cross_sections': cs_arch,
                      'arch_cross_sections_x': cs_arch_x, 'tie_cross_sections': cs_tie, 'tie_cross_sections_x': cs_tie_x,
                      'hangers_amount': n_hangers, 'hangers_arrangement': hanger_arrangement,
                      'hangers_parameters': hanger_params, 'hangers_cross_section': cs_hangers,
                      'cost_cross_sections': cost_cross_sections, 'unit_weight_anchorages': unit_weight_anchorages,
                      'unit_price_anchorages': unit_price_anchorages}
        self.span = span
        self.hangers_amount = n_hangers
        self.hangers_cross_section = cs_hangers
        self.cost_cross_sections = cost_cross_sections
        self.unit_weight_anchorages = unit_weight_anchorages
        self.unit_price_anchorages = unit_price_anchorages

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
        tie = Tie(nodes, span, n_floor_beams, g_deck, g_utilities)
        hangers = Hangers(nodes, hanger_set, span)

        # Define the arch shape (thrust line is obtained later)
        if arch_shape == 'Parabolic':
            arch = ParabolicArch(nodes, span, rise)
        elif arch_shape == 'Circular':
            arch = CircularArch(nodes, span, rise)
        elif arch_shape.startswith('Polynomial'):
            arch = QuarticArch(nodes, span, rise, float(arch_shape[11:]))
        elif arch_shape == 'Continuous optimisation':
            g_arch = cs_arch[1].weight
            g_tie = g_deck + g_utilities + cs_tie[1].weight
            arch = ContinuousArch(nodes, hanger_set, g_arch, g_tie, span, rise)
        else:
            raise Exception('Arch shape "' + arch_shape + '" is not defined.')

        # Connect the hangers to the tie and the arch
        tie.assign_hangers(hangers)
        arch.connect_nodes(nodes, hangers)

        # Define cross-sections
        arch.define_cross_sections(nodes, cs_arch_x, cs_arch)
        tie.define_cross_sections(nodes, cs_tie_x, cs_tie)
        hangers.assign_cross_section(cs_hangers)

        # Define the entire network arch structure
        network_arch = NetworkArch(arch, tie, hangers, nodes)

        # Determine the self equilibrium stress-state
        if self_stress_state == 'Zero-displacement':
            mz_0 = tie.zero_displacement(nodes, hangers, *self_stress_state_params[0:1])
            n_0 = arch.define_n_by_peak_moment(nodes, hangers, mz_0, *self_stress_state_params[1:])

        elif self_stress_state == 'Tie-optimisation':
            mz_0 = optimize_self_stresses_tie_1(tie, nodes, hangers, *self_stress_state_params[1:2])
            n_0 = arch.define_n_by_least_squares(nodes, hangers, mz_0)

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
            nodes.pop_nodes(arch.nodes[1:-1])
            g_arch = cs_arch[0].weight
            arch = ThrustLineArch(nodes, span, rise, g_arch, hangers)
            arch.connect_nodes(nodes, hangers)
            arch.define_cross_sections(nodes, cs_arch_x, cs_arch)
            n_0 = arch.define_n_by_least_squares(nodes, hangers, mz_0)
            network_arch.arch = arch

        if curve_fitting:
            nodes.pop_nodes(arch.nodes[1:-1])
            if curve_fitting.startswith('Polynomial'):
                arch = PolynomialArch(nodes, arch)
            if curve_fitting.startswith('Spline'):
                arch = SplineArch(nodes, arch, hangers)
            arch.connect_nodes(nodes, hangers)
            arch.define_cross_sections(nodes, cs_arch_x, cs_arch)
            if not curve_fitting.endswith('-n'):
                n_0 = arch.define_n_by_least_squares(nodes, hangers, mz_0)
            network_arch.arch = arch




        # Assign the permanent effects to the cross sections
        hangers.assign_length_to_cross_section()
        hangers.assign_permanent_effects()
        arch.assign_permanent_effects(nodes, hangers, n_0, -mz_0)
        tie.assign_permanent_effects(nodes, hangers, -n_0, mz_0)

        # Calculate the load cases
        network_arch.calculate_load_cases(q_ll_d, q_ll_c, qc_fatigue)
        network_arch.assign_wind_effects()
        network_arch.calculate_strength_limit_states()

        network_arch.calculate_cable_loss(cable_loss_events)

        network_arch.calculate_tie_fracture(q_ll_d, q_ll_c)

        self.nodes = nodes
        self.network_arch = network_arch

        self.cost = 0
        self.costs = 0
        self.cost_anchorages = 0
        self.cost_function()
        return

    def plot_elements(self, ax=None):
        if not ax:
            fig, ax = pyplot.subplots(1, 1, figsize=(4, 1.5), dpi=720)
        else:
            fig = ax.get_figure()
        model = {'Nodes': {'Location': [[0, 0], [self.span, 0]]},
                 'Boundary Conditions': {'Restricted Degrees': [[0, 1, 1, 0, 0], [1, 0, 1, 0, 0]]}}
        plot_supports_new(model, ax, factor=0.03)
        self.network_arch.tie.plot_elements(ax)
        self.network_arch.arch.plot_elements(ax)
        self.network_arch.hangers.plot_elements(ax)
        ax.set_aspect('equal', adjustable='box')
        ax.axis('off')
        return fig, ax

    def plot_effects_on_structure(self, name, key, ax=None):
        if not ax:
            fig, ax = self.plot_elements()
        else:
            fig = ax.get_figure()
        tie_max, tie_min = self.network_arch.tie.get_min_and_max(name, key)
        arch_max, arch_min = self.network_arch.arch.get_min_and_max(name, key)
        effect_amax = max(tie_max, -tie_min, arch_max, arch_min)
        self.network_arch.arch.plot_effects_on_structure(ax, name, key, reaction_amax=effect_amax)
        self.network_arch.tie.plot_effects_on_structure(ax, name, key, reaction_amax=effect_amax)
        self.network_arch.hangers.plot_elements(ax)
        return fig, ax

    def plot_effects(self, name, key, fig=None, dc=True, label='', c='black', lw=1.0, ls='-', marker='x'):
        if not fig:
            fig, axs = pyplot.subplots(2, 2, figsize=(8, 4), dpi=240)
        axs = fig.get_axes()
        self.network_arch.arch.plot_effects(axs[0], name, key, label=label, c=c, lw=lw, ls=ls)
        self.network_arch.tie.plot_effects(axs[1], name, key, label=label, c=c, lw=lw, ls=ls)
        self.network_arch.hangers.plot_effects(axs[2], name, dc=dc, label=label, c=c, lw=lw, ls=ls, marker=marker)
        return fig

    def plot_all_effects(self, name, fig=None, dc=True, label='', c='black', lw=1.0, ls='-', marker='x'):
        if not fig:
            fig, axs = pyplot.subplots(2, 3, figsize=(12, 4), dpi=240)
        axs = fig.get_axes()
        self.network_arch.arch.plot_effects(axs[0], name, 'Normal Force', label=label, c=c, lw=lw, ls=ls)
        self.network_arch.tie.plot_effects(axs[1], name, 'Normal Force', label=label, c=c, lw=lw, ls=ls)
        self.network_arch.hangers.plot_effects(axs[2], name, dc=dc, label=label, c=c, lw=lw, ls=ls,  marker=marker)
        self.network_arch.arch.plot_effects(axs[3], name, 'Moment', label=label, c=c, lw=lw, ls=ls)
        self.network_arch.tie.plot_effects(axs[4], name, 'Moment', label=label, c=c, lw=lw, ls=ls)
        return fig

    def internal_forces_table(self, name='design forces table', all_uls=False):
        uls_forces_table(name, self.cost_cross_sections, all_uls=all_uls)
        return

    def dc_ratio_table(self, name='dc table', uls_types=""):
        dc_table(name, self.cost_cross_sections, uls_types=uls_types)
        return

    def cost_table(self, name='cost table'):
        anchorages = (2 * self.hangers_amount, self.unit_weight_anchorages,
                      self.unit_price_anchorages, self.cost_anchorages)
        cost_table(name, self.cost_cross_sections, anchorages)
        print('Costs: $', round(self.cost / 1000) / 1000, 'Mio.')
        return

    def cost_function(self):
        costs = []
        for cross_section in self.cost_cross_sections:
            costs.append(cross_section.calculate_cost())
        hanger_cs = self.hangers_cross_section
        weight_anchorages = 2 * self.hangers_amount * self.unit_weight_anchorages
        self.cost_anchorages = weight_anchorages * self.unit_price_anchorages * hanger_cs.dc_max / hanger_cs.dc_ref
        costs.append(self.cost_anchorages)
        costs.append(50000)
        cost = sum(costs)
        self.costs = costs
        self.cost = cost
        return cost
