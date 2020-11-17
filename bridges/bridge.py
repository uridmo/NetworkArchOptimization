from structure_elements.arch.assign_arch_compression import define_by_peak_moment
from structure_elements.arch.parabolic_arch import ParabolicArch
from structure_elements.hangers.assign_hanger_forces import zero_displacement
from structure_elements.hangers.constant_change_hangers import ConstantChangeHangerSet
from structure_elements.hangers.hanger_set import mirror_hanger_set, Hangers
from structure_elements.hangers.parallel_hangers import ParallelHangerSet
from structure_elements.hangers.radial_hangers import RadialHangerSet
from structure_elements.networkarch import NetworkArch
from structure_elements.nodes.nodes import Nodes
from structure_elements.tie import Tie


class Bridge:
    def __init__(self, span, rise, n_cross_girders, g_deck, qd_live_load, qc_live_load,
                 arch_shape, cs_arch_x, cs_arch, reg_arch_x, reg_arch, cs_tie_x, cs_tie,
                 reg_tie_x, reg_tie, n_hangers, arrangement, hanger_params, cs_hangers,
                 strength_combination, cable_loss_combination):

        self.span = span
        self.rise = rise
        self.cross_girder_amount = n_cross_girders
        self.weight_deck = g_deck
        self.distributed_live_load = qd_live_load
        self.concentrated_live_load = qc_live_load
        self.arch_shape = arch_shape
        self.arch_cross_sections = cs_arch
        self.arch_cross_sections_x = cs_arch_x
        self.arch_regions = reg_arch
        self.arch_regions_x = reg_arch_x
        self.tie_cross_sections = cs_tie
        self.tie_cross_sections_x = cs_tie_x
        self.tie_regions = reg_tie
        self.tie_regions_x = reg_tie_x
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
        tie = Tie(nodes, span)
        arch = ParabolicArch(nodes, span, rise)

        # Assign the hangers to the tie
        tie.assign_hangers(hangers)
        arch.arch_connection_nodes(nodes, hangers)

        # Define cross-sections
        arch.define_cross_sections(nodes, cs_arch_x, cs_arch)
        tie.define_cross_sections(nodes, cs_tie_x, cs_tie)
        hangers.define_cross_section(cs_hangers)

        # Define regions
        arch.define_regions(nodes, reg_arch_x, reg_arch)
        tie.define_regions(nodes, reg_tie_x, reg_tie)

        # Assign the constraint moment and the hanger forces
        mz_0 = zero_displacement(tie, nodes, hangers, dof_rz=True, plot=False)
        hangers.assign_permanent_effects()

        # Determine the constraint tie tension force
        n_0 = define_by_peak_moment(arch, nodes, hangers, mz_0, peak_moment=-10 ** 3)

        # Calculate the states under permanent stresses
        arch.calculate_permanent_impacts(nodes, hangers, n_0, mz_0, plots=False, name='Arch Permanent Moment')
        tie.calculate_permanent_impacts(nodes, hangers, n_0, mz_0, plots=False, name='Tie Permanent Moment')

        # Define the entire network arch structure
        network_arch = NetworkArch(arch, tie, hangers)

        # Calculate the load cases
        network_arch.calculate_dead_load(nodes)
        network_arch.calculate_distributed_live_load(nodes, qd_live_load, 20, 40)
        network_arch.assign_range_to_sections()

        self.nodes = nodes
        self.network_arch = network_arch
        return

    def analyse(self):
        network_arch = self.tie_regions
        return network_arch
