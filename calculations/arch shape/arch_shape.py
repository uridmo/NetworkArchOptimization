import pickle

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.plots import make_plots

# Import the base case
f = open('../base case/bridge.pckl', 'rb')
bridge_ref = pickle.load(f)
f.close()
# bridge_ref = BlennerhassettBridge(arch_optimisation=False, self_stress_state='Overall-optimisation')


bridge_optimized = BlennerhassettBridge()
bridge_continuous = BlennerhassettBridge(arch_shape='Continuous optimisation', arch_optimisation=False,
                                         n_hangers=26, n_cross_girders=26)

bridges_dict = {'Final design': bridge_ref, 'Thrust line arch': bridge_optimized,
                'Continuous arch shape': bridge_continuous}
load_groups = {'permanent state': 'Permanent', 'strength-I': 'Strength-I', 'strength-III': 'Strength-III'}
make_plots(bridges_dict, load_groups)

bridge_optimized.cost_table()
bridge_optimized.dc_ratio_table()
bridge_optimized.internal_forces_table()
