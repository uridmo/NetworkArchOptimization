import tracemalloc

from matplotlib import pyplot

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.adjustments import adjust_overview_plots

tracemalloc.start()

colors = [(0.0000, 0.4470, 0.7410), (0.8500, 0.3250, 0.0980), (0.9290, 0.6940, 0.1250),
          (0.4940, 0.1840, 0.5560), (0.4660, 0.6740, 0.1880), (0.3010, 0.7450, 0.9330),
          (0.6350, 0.0780, 0.1840), (0.1840, 0.6350, 0.0780)]

blennerhassett_0 = BlennerhassettBridge(exact_cross_sections=False)
network_arch = blennerhassett_0.network_arch

network_arch.set_range('Permanent + -1 DL', 'PRE')
fig = network_arch.plot_effects('Permanent', 'Moment', color=colors[0])
fig = network_arch.plot_effects('DL', 'Moment', fig=fig, color=colors[1])
fig = network_arch.plot_effects('PRE', 'Moment', fig=fig, color=colors[2])
adjust_overview_plots(fig)
pyplot.show()

fig = network_arch.plot_effects('LL', 'Moment', color=colors[0])
adjust_overview_plots(fig)
pyplot.show()


# network_arch.set_range('PRE, 0.9 DL/1.35 DL, 1.75 LL', 'Strength')
# fig = network_arch.plot_effects('Strength', 'Moment', color=colors[0])
# adjust_overview_plots(fig)
# pyplot.show()

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")
tracemalloc.stop()
