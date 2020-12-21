import numpy as np
from matplotlib import pyplot
from plotting.loads import plot_loads

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.save import save_plot

bridge_parallel = BlennerhassettBridge(arch_optimisation=False)

self = bridge_parallel.network_arch
i_hanger = 3
ll_factor = 1.5
name = 'Cable_Replacement'
q_d = 18.3
q_c = 900

hanger = self.hangers[i_hanger]
span = self.tie.span
n = self.tie.cross_girders_amount
f_d = span * q_d / (n + 1)

# Find worst load arrangement
self.set_range('EL + 1.2 DC + 1.4 DW', 'Cable loss')
load = '0'
max_hanger_force = 0
max_hanger_force_i = 0
for i in range(len(self.tie.cross_girders_nodes)):
    hanger_force = hanger.effects_N['F' + str(i + 1)]
    if hanger_force > 0:
        load += ' + ' + str(f_d) + ' F' + str(i + 1)
    if hanger_force > max_hanger_force:
        max_hanger_force = hanger_force
        max_hanger_force_i = i
load += ' + ' + str(q_c) + ' F' + str(max_hanger_force_i + 1)
effects = self.get_effects(load)
self.set_effects(effects, 'LL_' + name)
effects = self.get_effects('EL + 1.2 DC + 1.4 DW + ' + str(ll_factor) + ' LL_' + name)
self.set_effects(effects, name + '_static')
hanger_force = hanger.effects_N[name + '_static']

model = self.create_model()
i_tie = len(self.tie)
i_arch = i_tie + len(self.arch)
i = i_arch + i_hanger
model['Beams']['Nodes'].pop(i)
model['Beams']['Stiffness'].pop(i)
model['Beams']['Releases'] = model['Beams']['Releases'][:-1]

vertical_force = hanger_force * np.sin(hanger.inclination)
horizontal_force = hanger_force * np.cos(hanger.inclination)
loads_nodal = [[hanger.tie_node.index, -horizontal_force, -vertical_force, 0],
               [hanger.arch_node.index, horizontal_force, vertical_force, 0]]
model['Loads'] = [{'Nodal': loads_nodal}]

loads_nodal = [[bridge_parallel.network_arch.tie.cross_girders_nodes[i_hanger].index, 0, -900, 0]]
for i in range(5):
    loads_nodal.append([bridge_parallel.network_arch.tie.cross_girders_nodes[i].index, 0, -350, 0])
model['Loads'].append({'Nodal': loads_nodal})
fig, ax = bridge_parallel.plot_elements()
plot_loads(model, 1, ax)
pyplot.show()
save_plot(fig, 'figures', 'cable loss - load arrangement')

bridge_parallel.network_arch.hangers.hanger_sets[0].hangers.pop(i_hanger)
fig, ax = bridge_parallel.plot_elements()
plot_loads(model, 0, ax, max_length=1/20)
pyplot.show()
save_plot(fig, 'figures', 'cable loss')

