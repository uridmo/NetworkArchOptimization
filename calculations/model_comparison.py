from bridges.Blennerhassett import BlennerhassettBridge
from plotting.plots import make_plots


bridge_basic = BlennerhassettBridge(self_stress_state='Zero-displacement', knuckles=False, exact_stiffness=False)
bridge_stiffness = BlennerhassettBridge(self_stress_state='Zero-displacement', knuckles=False, exact_stiffness=True)
bridge_knuckle = BlennerhassettBridge(self_stress_state='Zero-displacement', knuckles=True, exact_stiffness=False)

bridges_dict = {'Basic model': bridge_basic, 'Accurate stiffness': bridge_stiffness, 'Accurate Knuckles': bridge_knuckle}
load_groups = {'live loading': 'LL'}
folder = 'model comparison'
make_plots(bridges_dict, load_groups, folder)
