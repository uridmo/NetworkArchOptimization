import pickle

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.plots import make_plots

# Import the base case
f = open('base case/bridge.pckl', 'rb')
bridge_ref = pickle.load(f)
f.close()

bridge_optimized = BlennerhassettBridge()

bridges_dict = {'Base case': bridge_ref, 'Optimized': bridge_optimized}
load_groups = {'permanent state': 'Permanent', 'strength-I': 'Strength-I'}
folder = 'first optimisation'
make_plots(bridges_dict, load_groups, folder)

bridge_optimized.cost_table(folder)
bridge_optimized.dc_ratio_table(folder)
bridge_optimized.internal_forces_table(folder)
