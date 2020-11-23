import tracemalloc

from matplotlib import pyplot

from bridges.Blennerhassett.Blennerhassett import BlennerhassettBridge
from plotting.adjustments import adjust_overview_plots, adjust_small_plots
from plotting.save import save_plot

tracemalloc.start()

colors = [(0.0000, 0.4470, 0.7410), (0.8500, 0.3250, 0.0980), (0.9290, 0.6940, 0.1250),
          (0.4940, 0.1840, 0.5560), (0.4660, 0.6740, 0.1880), (0.3010, 0.7450, 0.9330),
          (0.6350, 0.0780, 0.1840), (0.1840, 0.6350, 0.0780)]

bridge_ref = BlennerhassettBridge(exact_cross_sections=False)

bridge_ref.network_arch.set_range('Permanent + -1 DL', 'PRE')


fig = bridge_ref.plot_all_effects('Permanent', label='Reference calculation', c=colors[0])
axs = fig.get_axes()
axs[0].axhline(-44.5, c=colors[1], lw=1)
axs[0].axhline(-38, c=colors[1], lw=1)
axs[1].axhline(36, c=colors[1], lw=1)
axs[1].axhline(34.5, c=colors[1], lw=1)
axs[2].axhline(2.420, c=colors[1], lw=1)
axs[2].axhline(1.600, c=colors[1], lw=1)
axs[3].axhline(3.69, c=colors[1], lw=1)
axs[3].axhline(-3.69, c=colors[1], lw=1)
axs[4].axhline(2.7, c=colors[1], lw=1)
axs[4].plot([0, 270], [-3.17, -3.17], label='Design drawings', c=colors[1], lw=1)
axs[5].remove()
handles, labels = axs[4].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.7, 0.45))
adjust_overview_plots(fig)
pyplot.show()
save_plot(fig, 'Drawings comparison', 'Permanent state')


hanger_forces = [0.4981984, 0.7517458, 0.7695386, 0.7295048, 0.6850228, 0.644989, 0.5827142, 0.5515768, 0.5070948,
                 0.467061, 0.4136826, 0.3603042, 0.3514078]
hanger_x = [267.8*(i+1)/14 for i in range(13)]


fig = bridge_ref.plot_effects('LL', 'Moment', label='Reference calculation', c=colors[0])
axs = fig.get_axes()
axs[1].plot([0, 270], [4.73, 4.73], label='Design drawings', c=colors[1], lw=1)
axs[2].plot(hanger_x, hanger_forces, label='Design drawings', c=colors[1])
axs[3].remove()
handles, labels = axs[1].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.55, 0.45))

adjust_small_plots(fig)
pyplot.show()
save_plot(fig, 'Drawings comparison', 'Live load')


current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
tracemalloc.stop()
