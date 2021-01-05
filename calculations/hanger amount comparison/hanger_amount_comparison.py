from bridges.Blennerhassett import BlennerhassettBridge
from plotting.plots import make_plots, arch_or_tie_plots
from plotting.tables import dc_overview_table, small_cost_overview_table

bridge_13 = BlennerhassettBridge()
bridge_20 = BlennerhassettBridge(n_hangers=20)
bridge_27 = BlennerhassettBridge(n_hangers=27)

adapted_params = (1.0646, False, 267.8/(4*14))
bridge_26 = BlennerhassettBridge(hanger_params=adapted_params, n_hangers=26)
bridge_26.plot_elements()

bridges_dict = {'13 Hangers': bridge_13, '20 Hangers': bridge_20, '26 Hangers': bridge_26, '27 Hangers': bridge_27}
load_groups = {'permanent state': 'Permanent', 'dead load': 'DL', 'live loading': 'LL'}
make_plots(bridges_dict, load_groups, marker='')

load_groups = {'tie fracture': 'Tie Fracture'}
arch_or_tie_plots(bridges_dict, load_groups, arch=False)

small_cost_overview_table('cost_comparison', bridges_dict)
dc_overview_table('dc_comparison', bridges_dict)
