import tracemalloc

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.plots import make_plots

tracemalloc.start()

bridge_13 = BlennerhassettBridge()
bridge_20 = BlennerhassettBridge(n_hangers=20, n_cross_girders=20)
bridge_27 = BlennerhassettBridge(n_hangers=27, n_cross_girders=27)

bridges_dict = {'13 Deck beams': bridge_13, '20 Deck beams': bridge_20, '27 Deck beams': bridge_27}
load_groups = {'permanent state': 'Permanent', 'live loading': 'LL', 'dead load range': '0.25 DC/-0.1 DC, 0.5 DW/-0.35 DW'}
folder = 'deck beam comparison'
make_plots(bridges_dict, load_groups, folder, big_plots=True)

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
tracemalloc.stop()
