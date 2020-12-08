from bridges.Blennerhassett import BlennerhassettBridge
from plotting.plots import make_plots

bridge_13 = BlennerhassettBridge()
bridge_20 = BlennerhassettBridge(n_hangers=20, n_cross_girders=20)
bridge_27 = BlennerhassettBridge(n_hangers=27, n_cross_girders=27)

bridges_dict = {'13 Floor beams': bridge_13, '20 Floor beams': bridge_20, '27 Floor beams': bridge_27}
load_groups = {'permanent state': 'Permanent', 'live loading': 'LL',
               'dead load range': '0.25 DC/-0.1 DC, 0.5 DW/-0.35 DW',
               'strength-I': 'Strength-I'}
folder = 'floor beam comparison'
make_plots(bridges_dict, load_groups, folder, big_plots=True)

bridge_13.cost_table(folder, name='cost table 13 floor beams')
bridge_20.cost_table(folder, name='cost table 20 floor beams')
bridge_27.cost_table(folder, name='cost table 27 floor beams')
