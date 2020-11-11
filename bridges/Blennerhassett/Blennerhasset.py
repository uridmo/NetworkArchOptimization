import numpy as np

from structure_elements.arch.assign_arch_compression import define_by_peak_moment
from structure_elements.arch.circular_arch import CircularArch
from structure_elements.arch.parabolic_arch import ParabolicArch
from structure_elements.hangers.parallel_hangers import ParallelHangerSet
from structure_elements.hangers.hangers import mirror_hanger_set
from structure_elements.hangers.radial_hangers import RadialHangerSet
from structure_elements.nodes.nodes import Nodes
from structure_elements.tie import Tie
from structure_elements.networkarch import NetworkArch
from structure_elements.hangers.assign_hanger_forces import zero_displacement

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
hangers.assign_stiffness(ea_hangers, ei_hangers)

# Create the tie
tie = Tie(nodes, span, g_tie, ea_tie, ei_tie)
tie.assign_hangers(hangers)

# Assign the constraint moment and the hanger forces
mz_0 = zero_displacement(tie, nodes, save_plot=True)

# Create the arch and get the connection to the hangers
arch = CircularArch(nodes, span, rise, g_arch, ea_arch, ei_arch)
arch.arch_connection_nodes(nodes, hangers)

# Determine the constraint tie tension force
n_0 = define_by_peak_moment(arch, nodes, hangers, mz_0, peak_moment=-10 ** 6)

# Calculate the states under permanent stresses
arch.calculate_permanent_impacts(nodes, hangers, n_0, mz_0, plots=False)
tie.calculate_permanent_impacts(nodes, hangers, n_0, mz_0, plots=False)

# arch.plot_internal_force(nodes, 'Moment')

# Define the entire network arch structure
network_arch = NetworkArch(arch, tie, hangers)
network_arch.create_model(nodes, plot=True)
