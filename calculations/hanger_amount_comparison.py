import tracemalloc

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.plots import make_plots

tracemalloc.start()

bridge_13 = BlennerhassettBridge(self_stress_state='Zero-displacement', arch_optimisation=True)
bridge_20 = BlennerhassettBridge(n_hangers=20, self_stress_state='Tie-optimisation', arch_optimisation=True)

adapted_params = (1.0646, False, 267.8/(4*14))
bridge_27 = BlennerhassettBridge(hanger_params=adapted_params, n_hangers=26, self_stress_state='Tie-optimisation', arch_optimisation=True)

bridge_27.plot_elements()

bridges_dict = {'13 Hangers': bridge_13, '20 Hangers': bridge_20, '27 Hangers': bridge_27}
load_groups = {'permanent state': 'Permanent', 'live loading': 'LL'}
folder = 'hanger amount comparison'
make_plots(bridges_dict, load_groups, folder, big_plots=True)

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
tracemalloc.stop()
