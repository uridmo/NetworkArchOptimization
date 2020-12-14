from bridges.Blennerhassett import BlennerhassettBridge
from plotting.plots import make_plots
from plotting.tables import small_cost_overview_table

bridge_13 = BlennerhassettBridge()
bridge_27 = BlennerhassettBridge(n_hangers=27)

adapted_params = (1.0646, False, 267.8/(4*14))
bridge_26 = BlennerhassettBridge(hanger_params=adapted_params, n_hangers=26)
bridge_26.plot_elements()

bridges_dict = {'13 Hangers': bridge_13, '26 Hangers': bridge_26, '27 Hangers': bridge_27}
load_groups = {'permanent state': 'Permanent', 'dead load': 'DL', 'live loading': 'LL'}
folder = 'hanger amount comparison'
make_plots(bridges_dict, load_groups, folder)

small_cost_overview_table(folder, 'cost comparison', bridges_dict)
