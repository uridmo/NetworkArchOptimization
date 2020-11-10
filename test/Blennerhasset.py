import numpy as np

from arch.parabolic_arch import ParabolicArch
from arch.continuous_arch import ContinuousArch
from hangers.parallel_hangers import ParallelHangerSet
from hangers.radial_hangers import RadialHangerSet
from hangers.hangers import mirror_hanger_set

from nodes.nodes import Nodes

from tie.tie import Tie
from hangers.assign_hanger_forces import assign_hanger_forces_zero_displacement

span = 267.8
rise = 53.5
q_tie = 178.1
q_arch = 32.1
n_hangers = 15
alpha = np.radians(45)
beta = np.radians(30)

# Initialize nodes
nodes = Nodes()

hanger_set = ParallelHangerSet(nodes, span, alpha, n_hangers)
hangers = mirror_hanger_set(nodes, hanger_set, span)

tie = Tie(nodes, span, hangers)

mz_0 = assign_hanger_forces_zero_displacement(tie, nodes, q_tie, 1000, 100)
tie.assign_stiffness(10 ** 6, 10 ** 7)

tie.calculate_permanent_impacts(nodes, q_tie, mz_0, plots=False)
# nodes.order_nodes()


arch = ParabolicArch(nodes, span, rise)
a = 1
arch.arch_connection_nodes(nodes, hangers)
b = 1
arch.assign_stiffness(10 ** 6, 10 ** 7)
arch.calculate_permanent_impacts(nodes, hangers, q_arch, mz_0, plots=True)
#
# print(hanger_set.hangers)
# hangers = mirror_hanger_set(hanger_set, span)
#
# print(hangers.hangers)
# print(arch.coordinates)