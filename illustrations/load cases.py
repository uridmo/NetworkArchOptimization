import numpy as np
from matplotlib import pyplot

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.loads import plot_loads
from plotting.save import save_plot
from structure_analysis import verify_input
from structure_elements.arch.parabolic_arch import ParabolicArch
from structure_elements.cross_section import CrossSection

hanger_params = (np.radians(63),)
bridge_parallel = BlennerhassettBridge(hanger_params=hanger_params, arch_optimisation=False)

fig, ax = bridge_parallel.plot_elements()
fig_2, ax_2 = bridge_parallel.plot_elements()
fig_3, ax_3 = bridge_parallel.plot_elements()
nodes = bridge_parallel.nodes

n_tie = len(bridge_parallel.network_arch.tie)
arch = ParabolicArch(nodes, 267.8, 53.5)
cs = CrossSection("", 29.8, [1, 1], [1, 1, 1])
arch.define_cross_sections(nodes, [267.8/2], [cs, cs])

bridge_parallel.network_arch.arch = arch

model = bridge_parallel.network_arch.create_model()

loads_arch = bridge_parallel.network_arch.arch.self_weight(n_tie)
loads_tie = bridge_parallel.network_arch.tie.self_weight()
loads_dc = [{'Distributed': loads_tie['Distributed'] + loads_arch['Distributed'], 'Nodal':loads_tie['Nodal']}]
model['Loads'] = loads_dc

model = verify_input(model)
plot_loads(model, 0, ax)
save_plot(fig, 'model overview', 'permanent loads')

model['Loads'] = [{'Nodal': model['Loads'][0]['Nodal']}]
plot_loads(model, 0, ax_2)
save_plot(fig_2, 'model overview', 'distributed live loads')

model['Loads'] = [{'Nodal': [model['Loads'][0]['Nodal'][1]]}]
plot_loads(model, 0, ax_3)
save_plot(fig_3, 'model overview', 'concentrated live loads')
pyplot.show()
