from matplotlib import pyplot

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.plots import make_plots

bridge_basic = BlennerhassettBridge(arch_optimisation=False)

fig, ax = bridge_basic.plot_effects_on_structure('-1 DL', 'Moment')
pyplot.show()
# fig.savefig('dead_load.png')
