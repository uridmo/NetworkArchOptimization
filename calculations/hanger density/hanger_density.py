from bridges.Blennerhassett import BlennerhassettBridge
from plotting.plots import make_plots, arch_or_tie_plots, crop_plots
from plotting.tables import dc_overview_table, small_cost_overview_table

bridge_13 = BlennerhassettBridge(curve_fitting='Polynomial')
bridge_20 = BlennerhassettBridge(n_hangers=20, curve_fitting='Polynomial')
bridge_27 = BlennerhassettBridge(n_hangers=27, curve_fitting='Polynomial')

adapted_params = (1.0646, False, 267.8/(4*14))
bridge_26 = BlennerhassettBridge(hanger_params=adapted_params, n_hangers=26, curve_fitting='Polynomial')
fig = bridge_26.plot_elements()[0]
fig.savefig('structure_26.png')

bridges_dict = {'13 Hangers per set': bridge_13, '20 Hangers per set': bridge_20, '26 Hangers per set': bridge_26,
                '27 Hangers per set': bridge_27}
load_groups = {'permanent': 'Permanent', 'dead loading': 'DL', 'live loading': 'LL', 'tie fracture': 'Tie Fracture'}
make_plots(bridges_dict, load_groups, marker='', all_labels=True, big_plots=True)
small_cost_overview_table('cost_comparison', bridges_dict)
dc_overview_table('dc_comparison', bridges_dict)

crop_plots('permanent', (3, 1), [3, 4, 2], (1, 4), (2920, 140))
crop_plots('dead loading', (3, 1), [3, 4, 2], (1, 4), (2920, 140))
crop_plots('tie fracture', (1, 1), [4], (1, 4), (1000, 140))


# load_groups = {'permanent state2': 'Permanent', 'tie fracture': 'Tie Fracture'}
# arch_or_tie_plots(bridges_dict, load_groups, arch=False)

