import numpy as np
from matplotlib import pyplot

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.general import colors
from plotting.plots import make_plots
from plotting.tables import small_cost_overview_table, big_cost_overview_table

bridge_13 = BlennerhassettBridge()
bridge_40 = BlennerhassettBridge(n_hangers=40, n_cross_girders=40)
bridge_27 = BlennerhassettBridge(n_hangers=27, n_cross_girders=27)
bridge_7 = BlennerhassettBridge(n_hangers=7, n_cross_girders=7)

bridge_7.plot_elements()

bridges_dict = {'7 Floor beams': bridge_7, '13 Floor beams': bridge_13, '27 Floor beams': bridge_27, '40 Floor beams': bridge_40}
load_groups = {'permanent state': 'Permanent', 'live loading': 'LL',
               'dead load range': '0.25 DC/-0.1 DC, 0.5 DW/-0.35 DW',
               'strength-I': 'Strength-I'}
folder = 'floor beam comparison'
make_plots(bridges_dict, load_groups, folder)
small_cost_overview_table(folder, 'cost comparison', bridges_dict)
big_cost_overview_table(folder, 'cost comparison big', bridges_dict)

hangers = []
cost_label = ['Arch cost', 'Tie cost', 'Hanger cost', 'Total cost']
costs = []
for n in [2,3,4,5,10,15,20,25,30,60]:
    bridge = BlennerhassettBridge(n_hangers=n, n_cross_girders=n)
    cost_arch = sum(bridge.costs[0:3]) / 10 ** 6
    cost_tie = sum(bridge.costs[3:6]) / 10 ** 6
    cost_hangers = sum(bridge.costs[6:9]) / 10 ** 6
    hangers.append([n])
    costs.append([cost_arch, cost_tie, cost_hangers, bridge.cost / 10**6])
fig = pyplot.figure()
ax = pyplot.subplot(111)
costs = np.array(costs)

for i in range(4):
    ax.plot(hangers, costs[:, i], label=cost_label[i], color=colors[i])

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_ylabel(r'Costs [$ Mio.]')
ax.set_ylim([0, 15])
ax.set_xlabel('Amount of hangers [-]')
ax.set_xlim([0, 60])
ax.legend(frameon=False)

pyplot.show()
print(1)
