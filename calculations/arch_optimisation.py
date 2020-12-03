import tracemalloc

from matplotlib import pyplot

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.adjustments import adjust_small_plots

tracemalloc.start()

# Test
colors = [(0.0000, 0.4470, 0.7410), (0.8500, 0.3250, 0.0980), (0.9290, 0.6940, 0.1250),
          (0.4940, 0.1840, 0.5560), (0.4660, 0.6740, 0.1880), (0.3010, 0.7450, 0.9330),
          (0.6350, 0.0780, 0.1840), (0.1840, 0.6350, 0.0780)]

bridge_13 = BlennerhassettBridge(exact_cross_sections=True, arch_optimisation=True)
fig = bridge_13.plot_effects('Permanent', 'Moment', label='13 Hangers', c=colors[0])
adjust_small_plots(fig)
pyplot.show()

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
tracemalloc.stop()
