import numpy as np

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.plots import make_plots, crop_plots
from plotting.tables import dc_overview_table, small_cost_overview_table

params = (np.radians(25),)
bridge_13_n = BlennerhassettBridge(arch_optimisation=True, curve_fitting='Spline')
bridge_13 = BlennerhassettBridge(hanger_arrangement='Radial', hanger_params=params, arch_shape='Circular', arch_optimisation=True, curve_fitting='Spline')
bridge_20 = BlennerhassettBridge(n_hangers=20, hanger_arrangement='Radial', hanger_params=params, arch_shape='Circular', arch_optimisation=True, curve_fitting='Spline')
bridge_26 = BlennerhassettBridge(n_hangers=26, hanger_arrangement='Radial', hanger_params=params, arch_shape='Circular', arch_optimisation=True, curve_fitting='Spline')

fig = bridge_26.plot_elements()[0]
fig.savefig('structure_26_radial.png')

bridges_dict = {'13 Parallel hangers': bridge_13_n, '13 Radial hangers': bridge_13,
                '20 Radial hangers': bridge_20, '26 Radial hangers': bridge_26}
load_groups = {'permanent': 'Permanent'}
make_plots(bridges_dict, load_groups, marker='')

# crop_plots('permanent', (3, 1), [3, 4, 2], (2, 2), (1000, 500))
# crop_plots('live loading', (3, 1), [3, 4, 2], (2, 2), (1000, 500))
# crop_plots('dead load', (3, 1), [3, 4, 2], (2, 2), (1000, 500))

small_cost_overview_table('cost_comparison', bridges_dict)
dc_overview_table('dc_comparison', bridges_dict)
