from bridges.Blennerhassett import BlennerhassettBridge
from plotting.plots import make_plots

# Import the base case
# f = open('base case/bridge.pckl', 'rb')
# bridge_ref = pickle.load(f)
# f.close()
self_stress_state_params = (-6*10**3,)
bridge_optimized_13 = BlennerhassettBridge(
                                           self_stress_state_params=self_stress_state_params)
bridge_optimized_13.plot_elements()
self_stress_state_params = (-0.5*10**3,)
bridge_optimized_27 = BlennerhassettBridge(arch_shape='Continuous optimisation', arch_optimisation=False,
                                           self_stress_state_params=self_stress_state_params,
                                           n_hangers=27, n_cross_girders=27)
bridge_1 = BlennerhassettBridge(arch_optimisation=False)

bridges_dict = {'Continuous optimisation 13': bridge_optimized_13, 'Continuous optimisation 27': bridge_optimized_27}  #, 'Parabolic': bridge_1}
load_groups = {'permanent state': 'Permanent'}
folder = 'arch optimisation'
make_plots(bridges_dict, load_groups, folder, big_plots=True)

# bridges_dict = {'Tie moment optimisation': bridge_1, 'Tie moment + arch moment optimisation': bridge_ref,
#                 'Tie moment + arch shape optimisation': bridge_optimized}
# load_groups = {'permanent state': 'Permanent'}
# folder = 'arch optimisation'
# make_plots(bridges_dict, load_groups, folder, big_plots=True)
#
# bridges_dict = {'Base case': bridge_ref, 'Optimized': bridge_optimized}
# load_groups = {'permanent state': 'Permanent', 'strength-I': 'Strength-I'}
# folder = 'first optimisation'
# make_plots(bridges_dict, load_groups, folder)
#
# bridge_optimized.cost_table(folder)
# bridge_optimized.dc_ratio_table(folder)
# bridge_optimized.internal_forces_table(folder)

# fig_size = (4, 1.5)
# dpi = 240
# fig = pyplot.figure(figsize=fig_size, dpi=dpi)
# ax = fig.add_subplot(111)
# bridge_optimized.plot_effects_on_structure(ax, 'LL', 'Moment')
# pyplot.show()
