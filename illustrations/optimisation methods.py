import numpy as np
from matplotlib import pyplot

from bridges.Blennerhassett import BlennerhassettBridge
# Plot model for zero-displacement method
from plotting.supports import plot_supports_new
from structure_analysis import structure_analysis
from structure_analysis.plotting import plot_loads_old, plot_internal_forces

bridge = BlennerhassettBridge(n_hangers=13, knuckles=False, self_stress_state='Zero-displacement',
                              arch_optimisation=False)

nodes = bridge.nodes
tie = bridge.network_arch.tie
arch = bridge.network_arch.arch
hangers = bridge.network_arch.hangers
hanger = hangers.hanger_sets[1].hangers[5]
hangers.hanger_sets = []

for node in nodes.nodes:
    if node.y > 0:
        node.y += 30
nodes.add_node(0, 30)
nodes.add_node(267.8, 30)

arch.nodes[0] = nodes.nodes[-2]
arch.nodes[-1] = nodes.nodes[-1]


model = bridge.network_arch.create_model()

s, c = np.sin(hanger.inclination), np.cos(hanger.inclination)
model['Loads'] = [{'Nodal': [[hanger.tie_node.index, c, s, 0],
                             [hanger.arch_node.index, -c, -s, 0]]}]
model['Boundary Conditions']['Restricted Degrees'] += [[len(nodes.nodes)-2, 1, 1, 0, 0],
                                                       [len(nodes.nodes)-1, 0, 1, 0, 0]]
d_tie, if_tie, rd_tie, sp_tie = structure_analysis(model)

print(max([max(test) for test in if_tie[0]['Moment']]))
print(min([min(test) for test in if_tie[0]['Moment']]))

effects = bridge.network_arch.internal_forces_to_effects(if_tie[0])
bridge.network_arch.set_effects(effects, 'Test')

fig, ax = bridge.plot_effects_on_structure('Test', 'Moment')
plot_supports_new(model, ax, factor=0.03)
fig.savefig('optimisation methods/overall optimisation single force moment.png')
pyplot.show()

plot_loads_old(model, 0, 'optimisation methods/overall optimisation single force', save_plot=True)
