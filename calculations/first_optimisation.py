import tracemalloc

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.adjustments import adjust_overview_plots
from plotting.save import save_plot
from plotting.colors import colors

tracemalloc.start()

hanger_params = (1.0646)
bridge_13 = BlennerhassettBridge(self_stress_state='Tie-optimisation', arch_optimisation=True)
fig = bridge_13.plot_all_effects('Permanent', label='13 Hangers', c=colors[0])
adjust_overview_plots(fig)
save_plot(fig, 'first optimisation', 'permanent state')

fig = bridge_13.plot_all_effects('LL', label='13 Hangers', c=colors[0])
adjust_overview_plots(fig)
save_plot(fig, 'first optimisation', 'live loading')

fig = bridge_13.plot_all_effects('Strength-I', label='13 Hangers', c=colors[0])
adjust_overview_plots(fig)
save_plot(fig, 'first optimisation', 'strength-i')

