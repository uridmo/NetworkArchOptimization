import numpy as np

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.plots import make_plots, crop_plots
from plotting.tables import dc_overview_table, small_cost_overview_table, big_cost_overview_table

bridge_parallel_85 = BlennerhassettBridge(hanger_params=(np.radians(85),))
bridge_parallel_75 = BlennerhassettBridge(hanger_params=(np.radians(75),))
bridge_parallel_65 = BlennerhassettBridge(hanger_params=(np.radians(65),))
fig, ax = bridge_parallel_65.plot_elements()
fig.savefig('arrangement_65.png')
bridge_parallel_55 = BlennerhassettBridge(hanger_params=(np.radians(55),))
bridge_parallel_45 = BlennerhassettBridge(hanger_params=(np.radians(45),))
fig, ax = bridge_parallel_45.plot_elements()
fig.savefig('arrangement_45.png')

bridges_dict = {'85° Arrangement': bridge_parallel_85, '75° Arrangement': bridge_parallel_75,
                '65° Arrangement': bridge_parallel_65, '55° Arrangement': bridge_parallel_55,
                '45° Arrangement': bridge_parallel_45}

load_groups = {'permanent': 'Permanent', 'live loading': 'LL',
               'dead load': 'DL', 'cable loss': 'Cable_Loss', 'cable loss 4': 'Cable_Loss_4'}
folder = 'hanger arrangement comparison'
make_plots(bridges_dict, load_groups, big_plots=True, all_labels=True, dc=False)

bridges_dict = {r'85\degree Arrangement': bridge_parallel_85, r'75\degree Arrangement': bridge_parallel_75,
                r'65\degree Arrangement': bridge_parallel_65, r'55\degree Arrangement': bridge_parallel_55,
                r'45\degree Arrangement': bridge_parallel_45}
dc_overview_table('dc_comparison', bridges_dict)
small_cost_overview_table('cost_comparison', bridges_dict)
big_cost_overview_table('cost_comparison_big', bridges_dict)

crop_plots('permanent', (3, 1), [0, 1, 2], (3, 2), (800, 500))
crop_plots('dead load', (3, 2), [0, 1, 2, 3, 4], (1, 5), (2042, 550), i_skip_label=[1, 4], i_skip_title=[3, 4])
crop_plots('live loading', (3, 1), [3, 4, 2], (3, 2), (800, 500))
crop_plots('cable loss 4', (3, 1), [3, 4, 2], (3, 2), (800, 500))