import numpy as np
from matplotlib import pyplot

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.general import colors
from plotting.plots import make_plots
from plotting.tables import small_cost_overview_table, big_cost_overview_table, dc_overview_table

bridge_7 = BlennerhassettBridge(n_hangers=7, n_cross_girders=7)
bridge_13 = BlennerhassettBridge()
bridge_27 = BlennerhassettBridge(n_hangers=27, n_cross_girders=27)
bridge_40 = BlennerhassettBridge(n_hangers=40, n_cross_girders=40)

bridges_dict = {'7 Floor beams': bridge_7, '13 Floor beams': bridge_13, '27 Floor beams': bridge_27,
                '40 Floor beams': bridge_40}
load_groups = {'permanent state': 'Permanent', 'live loading': 'LL',
               'dead load range': '0.25 DC/-0.1 DC, 0.5 DW/-0.35 DW',
               'strength-I': 'Strength-I'}

make_plots(bridges_dict, load_groups)
dc_overview_table('dc comparison', bridges_dict)
big_cost_overview_table('cost comparison big', bridges_dict)

hangers = []
cost_label = ['Total cost', 'Tie cost', 'Hanger cost', 'Arch cost']
costs = []
for n in [1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 13, 16, 19, 22, 25, 30, 35, 50]:
    bridge = BlennerhassettBridge(n_hangers=n, n_cross_girders=n)
    cost_arch = sum(bridge.costs[0:3]) / 10 ** 6
    cost_tie = sum(bridge.costs[3:6]) / 10 ** 6
    cost_hangers = sum(bridge.costs[6:9]) / 10 ** 6
    hangers.append([n])
    costs.append([bridge.cost / 10 ** 6, cost_tie, cost_hangers, cost_arch])
fig = pyplot.figure(figsize=(6, 3), dpi=240)
ax = pyplot.subplot(111)
costs = np.array(costs)

for i in range(4):
    ax.plot(hangers, costs[:, i], label=cost_label[i], color=colors[i])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_ylabel(r'Costs [$ Mio.]')
ax.set_ylim([0, 16])
ax.set_xlim([0, 50])
ax.set_yticks([0, 4, 8, 12, 16])
ax.set_xlabel('Amount of hangers per set [-]')

ax.legend(frameon=False)
fig.savefig('cost comparison.png')
pyplot.show()
