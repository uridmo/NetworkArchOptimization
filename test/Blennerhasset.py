import numpy as np

from arch.parabolic_arch import ParabolicArch
from arch.continuous_arch import ContinuousArch

from hangers.parallel_hangers import ParallelHangerSet
from hangers.radial_hangers import RadialHangerSet
from hangers.hangers import mirror_hanger_set

from nodes.nodes import Nodes

from tie.tie import Tie
from networkarch.networkarch import NetworkArch
from hangers.assign_hanger_forces import assign_hanger_forces_zero_displacement

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
beta = np.radians(30)

# Initialize nodes and create hanger set
nodes = Nodes()
hanger_set = ParallelHangerSet(nodes, span, alpha, n_hangers)


hangers = mirror_hanger_set(nodes, hanger_set, span)
hangers.assign_stiffness(ea_hangers, ei_hangers)

tie = Tie(nodes, span, hangers, ea_tie, ei_tie, g_tie)

mz_0 = assign_hanger_forces_zero_displacement(tie, nodes)

tie.calculate_permanent_impacts(nodes, 0, mz_0, plots=False)
# nodes.order_nodes()


arch = ParabolicArch(nodes, span, rise, g_arch, ea_arch, ei_arch)
arch.arch_connection_nodes(nodes, hangers)

arch.calculate_permanent_impacts(nodes, hangers, g_arch, mz_0, plots=True)


network_arch = NetworkArch(arch, tie, hangers)
network_arch.network_arch_structure(nodes, plot=True)
