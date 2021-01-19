import numpy as np
from matplotlib import pyplot
from plotting.general import colors

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.adjustments import adjust_plot

bridge_100 = BlennerhassettBridge(arch_optimisation=False, arch_shape='Polynomial 1.00')
bridge_95 = BlennerhassettBridge(arch_optimisation=False, arch_shape='Polynomial 0.95')
bridge_90 = BlennerhassettBridge(arch_optimisation=False, arch_shape='Polynomial 0.9')
bridge_85 = BlennerhassettBridge(arch_optimisation=False, arch_shape='Polynomial 0.85')
bridge_80 = BlennerhassettBridge(arch_optimisation=False, arch_shape='Polynomial 0.8')
bridge_c = BlennerhassettBridge(arch_optimisation=False, arch_shape='Circular')


bridges_dict = {'Parabolic arch': bridge_100,
                'Polynomial arch (b=0.95)': bridge_95,
                'Polynomial arch (b=0.90)': bridge_90,
                'Polynomial arch (b=0.85)': bridge_85,
                'Polynomial arch (b=0.80)': bridge_80,
                'Circular arch': bridge_c}

span = 267.8
rise = 53.5
fig, axs = pyplot.subplots(1, 2, figsize=(8, 2), dpi=240)
for i, key in enumerate(bridges_dict):
    bridge = bridges_dict[key]
    nodes = bridge.network_arch.arch.nodes
    x = np.array([node.x for node in nodes])
    y = np.array([node.y for node in nodes])
    y_ref = [rise * (1 - ((x_i - span / 2) / (span / 2)) ** 2) for x_i in x]
    axs[0].plot(x, y-y_ref, label=key, c=colors[i], lw=0.7)

axs[0].set_title('Arch shape')
axs[0].set_ylabel('Deviation [m]')
adjust_plot(axs[0], step=0.2, min_0=True)

axs[1].remove()
handles, labels = axs[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.55, 0.85), frameon=False)
fig.savefig('polynomial shapes.png')
pyplot.show()
