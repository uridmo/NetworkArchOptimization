import tracemalloc

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.adjustments import adjust_small_plots, adjust_overview_plots
from plotting.save import save_plot
from plotting.colors import colors

tracemalloc.start()

hanger_params = (1.0646,)
bridge_13 = BlennerhassettBridge(self_stress_state='Zero-displacement', arch_optimisation=True)
bridge_20 = BlennerhassettBridge(hanger_params=hanger_params, n_hangers=20, self_stress_state='Tie-optimisation', arch_optimisation=True)
bridge_27 = BlennerhassettBridge(hanger_params=hanger_params, n_hangers=27, self_stress_state='Tie-optimisation', arch_optimisation=True)

bridge_27.plot_elements()

fig = bridge_13.plot_all_effects('Permanent', label='13 Hangers', c=colors[0])
fig = bridge_20.plot_all_effects('Permanent', fig=fig, label='20 Hangers', c=colors[1])
fig = bridge_27.plot_all_effects('Permanent', fig=fig, label='27 Hangers', c=colors[2])
adjust_overview_plots(fig)
save_plot(fig, 'Hanger amount comparison', 'Permanent state')

fig = bridge_13.plot_effects('LL', 'Moment', label='13 Hangers', c=colors[0])
fig = bridge_20.plot_effects('LL', 'Moment', fig=fig, label='20 Hangers', c=colors[1])
fig = bridge_27.plot_effects('LL', 'Moment', fig=fig, label='27 Hangers', c=colors[2])
adjust_small_plots(fig)
save_plot(fig, 'Hanger amount comparison', 'Live load')



current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
tracemalloc.stop()
