import tracemalloc

from matplotlib import pyplot

from bridges.Blennerhassett.Blennerhassett import BlennerhassettBridge
from plotting.adjustments import adjust_overview_plots, adjust_small_plots
from plotting.save import save_plot

tracemalloc.start()

colors = [(0.0000, 0.4470, 0.7410), (0.8500, 0.3250, 0.0980), (0.9290, 0.6940, 0.1250),
          (0.4940, 0.1840, 0.5560), (0.4660, 0.6740, 0.1880), (0.3010, 0.7450, 0.9330),
          (0.6350, 0.0780, 0.1840), (0.1840, 0.6350, 0.0780)]

bridge_13 = BlennerhassettBridge(exact_cross_sections=True)
bridge_15 = BlennerhassettBridge(exact_cross_sections=True, n_hangers=20)
bridge_100 = BlennerhassettBridge(exact_cross_sections=True, n_hangers=100)


fig = bridge_13.plot_effects('DL', 'Moment', label='13 Hangers', c=colors[0])
fig = bridge_15.plot_effects('DL', 'Moment', fig=fig, label='20 Hangers', c=colors[1])
fig = bridge_100.plot_effects('DL', 'Moment', fig=fig, label='100 Hangers', c=colors[2])
axs = fig.get_axes()
axs[3].remove()
handles, labels = axs[1].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.55, 0.45))
adjust_small_plots(fig)
pyplot.show()
save_plot(fig, 'Hanger comparison', 'Dead load')


fig = bridge_13.plot_effects('LL', 'Moment', label='13 Hangers', c=colors[0])
fig = bridge_15.plot_effects('LL', 'Moment', fig=fig, label='20 Hangers', c=colors[1])
fig = bridge_100.plot_effects('LL', 'Moment', fig=fig, label='100 Hangers', c=colors[2])
axs = fig.get_axes()
axs[3].remove()
handles, labels = axs[1].get_legend_handles_labels()
fig.legend(handles[0::2], labels[0::2], loc='upper left', bbox_to_anchor=(0.55, 0.45))
adjust_small_plots(fig)
pyplot.show()
save_plot(fig, 'Hanger comparison', 'Live load')

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
tracemalloc.stop()
