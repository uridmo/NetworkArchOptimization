from matplotlib import pyplot

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.adjustments import adjust_overview_plots
from plotting.plots import make_plots


bridge_optimized = BlennerhassettBridge()
bridge_optimized.plot_elements()

# bridge_optimized.internal_forces_table(all_uls=True)
# bridge_optimized.dc_ratio_table()
# bridge_optimized.cost_table()

fig = bridge_optimized.plot_all_effects('LL', label='New', c='blue')
adjust_overview_plots(fig)

# fig = bridge_optimized.plot_all_effects('Cable_Replacement', label='New', c='blue')
# fig = bridge_optimized.plot_all_effects('Cable_Replacement_1', fig=fig, label='Old', c='red')
# adjust_overview_plots(fig)


#
# fig, axs = pyplot.subplots(2, 2, figsize=(8, 4), dpi=240)
# axs = fig.get_axes()
# bridge_optimized.network_arch.tie.plot_effects(axs[0], 'Tie Fracture', 'Web')
# bridge_optimized.network_arch.tie.plot_effects(axs[1], 'Tie Fracture', 'Top')
# bridge_optimized.network_arch.tie.plot_effects(axs[2], 'Tie Fracture', 'Bottom')
#
# pyplot.show()
#
# # bridges_dict = {'Final design': bridge_ref, 'Thrust line arch': bridge_optimized,
#                 'Continuous arch shape': bridge_continuous}
# load_groups = {'permanent state': 'Permanent', 'strength-I': 'Strength-I', 'strength-III': 'Strength-III'}
# make_plots(bridges_dict, load_groups)
