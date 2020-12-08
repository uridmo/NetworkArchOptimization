from bridges.Blennerhassett import BlennerhassettBridge
from plotting.plots import make_plots

bridge_13 = BlennerhassettBridge()
bridge_27 = BlennerhassettBridge(n_hangers=27)

adapted_params = (1.0646, False, 267.8/(4*14))
bridge_26 = BlennerhassettBridge(hanger_params=adapted_params, n_hangers=26)
bridge_26.plot_elements()

bridges_dict = {'13 Hangers': bridge_13, '27 Hangers': bridge_27, '26 Hangers': bridge_26}
load_groups = {'permanent state': 'Permanent', 'live loading': 'LL'}
folder = 'hanger amount comparison'
make_plots(bridges_dict, load_groups, folder, big_plots=True)

bridge_13.cost_table(folder, name='cost table 13 hangers')
bridge_27.cost_table(folder, name='cost table 27 hangers')
bridge_26.cost_table(folder, name='cost table 26 hangers')
