from bridges.Blennerhassett import BlennerhassettBridge
from plotting.plots import make_plots


bridge_basic = BlennerhassettBridge(arch_optimisation=False, knuckles=False, exact_stiffness=False)
bridge_stiffness = BlennerhassettBridge(arch_optimisation=False, knuckles=False, exact_stiffness=True)
bridge_knuckle = BlennerhassettBridge(arch_optimisation=False, knuckles=True, exact_stiffness=False)

bridges_dict = {'Simplistic model': bridge_basic, 'Accurate stiffness': bridge_stiffness, 'Accurate Knuckles': bridge_knuckle}
load_groups = {'dead_loading': 'DL'}
folder = 'model comparison'
make_plots(bridges_dict, load_groups, lw=0.7)
