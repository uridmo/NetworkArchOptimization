import numpy as np
from matplotlib import pyplot

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.loads import plot_loads
from plotting.supports import plot_supports_new

bridge_parallel = BlennerhassettBridge(knuckles=False, arch_optimisation=False)
nodes = bridge_parallel.nodes
hangers = bridge_parallel.network_arch.hangers

fig_1, ax_1 = pyplot.subplots(1, 1, figsize=(4, 1.5), dpi=720)
fig_2, ax_2 = pyplot.subplots(1, 1, figsize=(4, 1.5), dpi=720)

model = {'Nodes': {'Location': [[0, 0], [267.8, 0]]},
         'Boundary Conditions': {'Restricted Degrees': [[0, 1, 1, 0, 0], [1, 0, 1, 0, 0]]}}
plot_supports_new(model, ax_1, factor=0.03)
plot_supports_new(model, ax_2, factor=0.03)
ax_1.set_aspect('equal', adjustable='box')
ax_1.axis('off')

bridge_parallel.network_arch.hangers.plot_elements(ax_1)

pyplot.show()

ax_2.set_aspect('equal', adjustable='box')
ax_2.axis('off')

bridge_parallel.network_arch.arch.plot_elements(ax_1)
bridge_parallel.network_arch.tie.plot_elements(ax_2)

model = bridge_parallel.network_arch.create_model()
loads_arch = {'Nodal': [[13, 0, 0, -1], [14, -2, 0, 1]]}
loads_tie = {'Nodal': [[13, 0, 0, 1], [14, 2, 0, -1, []]]}

for hanger in hangers:
    node = hanger.tie_node.index
    vertical_force = -1 * np.sin(hanger.inclination)
    horizontal_force = -1 * np.cos(hanger.inclination)
    loads_tie['Nodal'].append([node, horizontal_force, vertical_force, 0, []])

    node = hanger.arch_node.index
    vertical_force = 1 * np.sin(hanger.inclination)
    horizontal_force = 1 * np.cos(hanger.inclination)
    loads_arch['Nodal'].append([node, horizontal_force, vertical_force, 0, []])
model['Loads'] = [loads_arch, loads_tie]
plot_loads(model, 0, ax_1)
plot_loads(model, 1, ax_2)

pyplot.show()