import numpy as np
from matplotlib import pyplot

from structure_elements.arch.assign_arch_compression import define_by_peak_moment
from structure_elements.arch.circular_arch import CircularArch
from structure_elements.hangers.assign_hanger_forces import zero_displacement
from structure_elements.hangers.hangers import mirror_hanger_set
from structure_elements.hangers.parallel_hangers import ParallelHangerSet
from structure_elements.networkarch import NetworkArch
from structure_elements.nodes.nodes import Nodes
from structure_elements.tie import Tie

# Close all figures
pyplot.close('all')

# Geometry
span = 267.8
rise = 53.5

# Tie
ea_tie = 10 ** 6
ei_tie = 10 ** 7
g_tie = 178.1

# Arch
ea_arch = 10 ** 6
ei_arch = 10 ** 7
g_arch = 0

# Hangers
ea_hangers = 10 ** 3
ei_hangers = 10 ** 7
n_hangers = 15
alpha = np.radians(45)
beta = np.radians(35)

# Initialize nodes and create hanger set
nodes = Nodes()

# Define the hanger set
hanger_set = ParallelHangerSet(nodes, span, alpha, n_hangers)
# hanger_set = RadialHangerSet(nodes, span, rise, beta, n_hangers, skip=1)

# Mirror the hanger set and assign stiffness
hangers = mirror_hanger_set(nodes, hanger_set, span)
hangers.set_stiffness(ea_hangers, ei_hangers)

# Create the structural elements
tie = Tie(nodes, span, g_tie, ea_tie, ei_tie)
arch = CircularArch(nodes, span, rise, g_arch, ea_arch, ei_arch)

# Assign the hangers to the tie
tie.assign_hangers(hangers)
arch.arch_connection_nodes(nodes, hangers)

# Define regions
arch.define_region(nodes, [20, -20], ['1', '2', '1'])
tie.define_region(nodes, [], ['1'])

# Assign the constraint moment and the hanger forces
mz_0 = zero_displacement(tie, nodes, dof_rz=True, plot=False)
hangers.assign_permanent_effects()

# Determine the constraint tie tension force
n_0 = define_by_peak_moment(arch, nodes, hangers, mz_0, peak_moment=-10 ** 6)

# Calculate the states under permanent stresses
arch.calculate_permanent_impacts(nodes, hangers, n_0, mz_0, plots=False, name='Arch Permanent Moment')
tie.calculate_permanent_impacts(nodes, hangers, n_0, mz_0, plots=False, name='Tie Permanent Moment')

# Define the entire network arch structure
network_arch = NetworkArch(arch, tie, hangers)
network_arch.calculate_dead_load(nodes)


network_arch.set_range('0.9 DL/1.35 DL', 'Test')

network_arch.create_model(nodes, plot=False)

network_arch.calculate_distributed_live_load(nodes, 22, 5)
network_arch.assign_range_to_sections()


a=1