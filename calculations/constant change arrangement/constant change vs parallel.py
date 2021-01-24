import numpy as np

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.plots import make_plots, crop_plots
from plotting.tables import dc_overview_table, small_cost_overview_table, big_cost_overview_table
curve = ''
bridge_65 = BlennerhassettBridge(curve_fitting=curve, hanger_params=(np.radians(65),))
bridge_75_65 = BlennerhassettBridge(curve_fitting=curve, hanger_arrangement='Constant Change', hanger_params=(np.radians(75), np.radians(65)))
bridge_85_65 = BlennerhassettBridge(curve_fitting=curve, hanger_arrangement='Constant Change', hanger_params=(np.radians(85), np.radians(65)))
fig, ax = bridge_85_65.plot_elements()
fig.savefig('arrangement_85_45.png')

bridge_95_65 = BlennerhassettBridge(curve_fitting=curve, hanger_arrangement='Constant Change', hanger_params=(np.radians(95), np.radians(65)))
bridge_105_65 = BlennerhassettBridge(curve_fitting=curve, hanger_arrangement='Constant Change', hanger_params=(np.radians(105), np.radians(65)))
fig, ax = bridge_105_65.plot_elements()
fig.savefig('arrangement_105_25.png')


bridges_dict = {'105°-25° Arrangement': bridge_105_65,
                '95°-35° Arrangement': bridge_95_65,
                '85°-45° Arrangement': bridge_85_65,
                '75°-55° Arrangement': bridge_75_65,
                '65° Arrangement': bridge_65}

load_groups = {'permanent': 'Permanent', 'live loading': 'LL',
               'dead load': 'DL', 'cable loss': 'Cable_Loss', 'cable loss 4': 'Cable_Loss_4'}
folder = 'hanger arrangement comparison'
make_plots(bridges_dict, load_groups, big_plots=True, all_labels=True, dc=False)

dc_overview_table('dc_comparison', bridges_dict)
small_cost_overview_table('cost_comparison', bridges_dict)
big_cost_overview_table('cost_comparison_big', bridges_dict)

crop_plots('live loading', (2, 2), [3, 4, 2], (1, 5), (1000, 500))


# crop_plots('permanent', (3, 1), [0, 1, 2], (3, 2), (800, 500))
# crop_plots('dead load', (3, 2), [0, 1, 2, 3, 4], (1, 5), (2042, 550), i_skip_label=[1, 4], i_skip_title=[3, 4])
# crop_plots('live loading', (3, 1), [3, 4, 2], (3, 2), (800, 500))
# crop_plots('cable loss 4', (3, 1), [3, 4, 2], (3, 2), (800, 500))