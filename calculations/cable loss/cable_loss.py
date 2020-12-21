import numpy as np
from matplotlib import pyplot

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.adjustments import adjust_overview_plots, adjust_effects_plots
from plotting.general import colors

load_case = 'Cable_Loss'
x = []
m_arch = []
m_tie = []
doc_arch = []
doc_tie = []
n_hangers = []

# for i in range(13):
#     x.append((i+1)/14*267.8)
#     bridge = BlennerhassettBridge(x_lost_cable=(i+1)/14, knuckles=False, arch_optimisation=False)
#
#     m_arch_i = bridge.network_arch.arch.effects[load_case]['Moment']
#     doc_arch_i_1 = bridge.network_arch.arch.effects[load_case]['D/C_1']
#     doc_arch_i_2 = bridge.network_arch.arch.effects[load_case]['D/C_2']
#     m_tie_i = bridge.network_arch.tie.effects[load_case]['Moment']
#     doc_tie_i_1 = bridge.network_arch.tie.effects[load_case]['D/C_1']
#     doc_tie_i_2 = bridge.network_arch.tie.effects[load_case]['D/C_2']
#     n_hangers_i = bridge.network_arch.hangers.effects[load_case]['Normal Force'][:, 0:26]
#
#     m_arch.append([np.min(m_arch_i), np.max(m_arch_i)])
#     m_tie.append([np.min(m_tie_i), np.max(m_tie_i)])
#     n_hangers.append([np.max(n_hangers_i)])
#     doc_arch.append(np.max((doc_arch_i_1, -doc_arch_i_1, doc_arch_i_2, -doc_arch_i_2)))
#     doc_tie.append(np.max((doc_tie_i_1, -doc_tie_i_1, doc_tie_i_2, -doc_tie_i_2)))
#
# x = np.array(x)
# m_arch = np.array(m_arch)
# m_tie = np.array(m_tie)
# n_hangers = np.array(n_hangers)
# fig = pyplot.subplots(2, 2, figsize=(8, 4), dpi=360)[0]
# axs = fig.get_axes()
# axs[0].plot(x, m_arch/1000)
# axs[1].plot(x, m_tie/1000)
# axs[2].plot(x, n_hangers/1000)
# adjust_effects_plots(fig)
# fig.savefig(load_case.lower()+'_internal_forces.png')
#
# fig = pyplot.subplots(2, 2, figsize=(8, 4), dpi=360)[0]
# axs = fig.get_axes()
# axs[0].plot(x, doc_arch)
# axs[1].plot(x, doc_tie)
# axs[2].plot(x, n_hangers/4190)
# adjust_effects_plots(fig)
# fig.savefig(load_case.lower()+'_degree_of_compliance.png')

bridge = BlennerhassettBridge(x_lost_cable=7 / 14)
fig = bridge.plot_all_effects(load_case, label='Middle Hanger', c=colors[0])
adjust_overview_plots(fig)
fig.savefig(load_case.lower()+'_middle_hanger.png')

bridge.internal_forces_table(all_uls=True)
