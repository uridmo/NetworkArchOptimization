from bridges.Blennerhassett import BlennerhassettBridge
from plotting.plots import make_plots


hanger_params = (1.0646,)
bridge_13 = BlennerhassettBridge()

bridges_dict = {'13 Hangers': bridge_13}
load_groups = {'permanent state': 'Permanent', 'live loading': 'LL'}
folder = 'first optimisation'
make_plots(bridges_dict, load_groups, folder, big_plots=True)
