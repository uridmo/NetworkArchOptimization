import numpy as np

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.plots import make_plots

bridge_parallel = BlennerhassettBridge()
hanger_params = (np.radians(90), np.radians(60))
bridge_change = BlennerhassettBridge(hanger_arrangement='Constant Change', hanger_params=hanger_params)
hanger_params = (np.radians(25),)
self_stress_state_params = (0, (0.25/0.65, 0.4/0.65))
bridge_radial = BlennerhassettBridge(hanger_arrangement='Radial', hanger_params=hanger_params,
                                     self_stress_state_params=self_stress_state_params)

bridge_change.plot_elements()

bridges_dict = {'Parallel': bridge_parallel, 'Constant change': bridge_change, 'Radial': bridge_radial}
load_groups = {'permanent': 'Permanent', 'live loading': 'LL', 'strength-I': 'Strength-I'}
folder = 'hanger arrangement comparison'
make_plots(bridges_dict, load_groups, folder, big_plots=True)

bridge_parallel.cost_table(folder, name='cost table parallel')
bridge_change.cost_table(folder, name='cost table constant change')
bridge_radial.cost_table(folder, name='cost table radial')
