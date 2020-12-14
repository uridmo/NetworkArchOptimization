import numpy as np

from bridges.Blennerhassett import BlennerhassettBridge
# Plot model for zero-displacement method
from structure_analysis import structure_analysis
from structure_analysis.plotting import plot_loads_old, plot_internal_forces

bridge = BlennerhassettBridge(n_hangers=13, knuckles=False, self_stress_state='Overall-optimisation',
                              arch_optimisation=False)

nodes = bridge.nodes
tie = bridge.network_arch.tie
arch = bridge.network_arch.arch
hangers = bridge.network_arch.hangers
hanger = hangers.hanger_sets[1].hangers[5]
hangers.hanger_sets = []
model = bridge.network_arch.create_model(nodes)
beams_nodes, beams_stiffness = tie.get_beams()
# model['Beams']['Nodes'] = beams_nodes
# model['Beams']['Stiffness'] = beams_stiffness
model['Beams']['Releases'] = [[0, 1, 0], [len(beams_nodes) - 1, 0, 1]]
s, c = np.sin(hanger.inclination), np.cos(hanger.inclination)
model['Loads'] = [{'Nodal': [[hanger.tie_node.index, c, s, 0],
                             [hanger.arch_node.index, -c, -s, 0]]}]

d_tie, if_tie, rd_tie, sp_tie = structure_analysis(model)
plot_internal_forces(model, d_tie, if_tie, 0, 'Moment', 'title', show_extrema=False,
                     save_plot=False, scale_max=0.25)

# plot_model(model, tie)
plot_loads_old(model, 0, 'Test')
# fig = zero_displacement(tie, nodes, hangers, plot=True)
# save_plot(fig, 'optimisation methods', 'zero-displacement_bad')
print('End')

# tie.assign_permanent_effects()
