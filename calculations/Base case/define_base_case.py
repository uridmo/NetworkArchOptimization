import pickle
import tracemalloc

from matplotlib import pyplot

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.adjustments import adjust_overview_plots, adjust_effects_plots
from plotting.general import colors

# Monitor memory usage
tracemalloc.start()

# Calculate the base case
folder = 'base case'
bridge_ref = BlennerhassettBridge(arch_optimisation=False, self_stress_state='Overall-optimisation')

# Plot permanent state and compare to design drawings
fig = bridge_ref.plot_all_effects('Permanent', label='Base case', c=colors[0])
axs = fig.get_axes()
axs[0].axhline(-44.5, c=colors[1], lw=1)
axs[0].axhline(-38, c=colors[1], lw=1)
axs[1].axhline(36, c=colors[1], lw=1)
axs[1].axhline(34.5, c=colors[1], lw=1)
axs[2].axhline(2.420/4.19, c=colors[1], lw=1)
axs[2].axhline(1.600/4.19, c=colors[1], lw=1)
axs[3].axhline(3.69, c=colors[1], lw=1)
axs[3].axhline(-3.69, c=colors[1], lw=1)
axs[4].axhline(2.7, c=colors[1], lw=1)
axs[4].plot([0, 270], [-3.17, -3.17], label='Design drawings', c=colors[1], lw=1)
adjust_overview_plots(fig)
fig.savefig('permanent state.png')

# Plot live loading range and compare to design drawings
fig = bridge_ref.plot_effects('LL', 'Moment', label='Base case', c=colors[0])
axs = fig.get_axes()
hanger_forces = [0.4981984, 0.7517458, 0.7695386, 0.7295048, 0.6850228, 0.644989, 0.5827142, 0.5515768, 0.5070948,
                 0.467061, 0.4136826, 0.3603042, 0.3514078]
hanger_forces = [hanger_force / 4.19 for hanger_force in hanger_forces]
hanger_x = [267.8*(i+1)/14 for i in range(13)]
axs[0].plot([0, 270], [0.744, 0.744], label='Design drawings', c=colors[1], lw=1)
axs[1].plot([0, 270], [4.73, 4.73], label='Design drawings', c=colors[1], lw=1)
axs[2].plot(hanger_x, hanger_forces, label='Design drawings', c=colors[1], marker='x')
adjust_effects_plots(fig)
fig.savefig('live load.png')

# Create table of internal forces and demand/capacity ratios
bridge_ref.internal_forces_table()
bridge_ref.internal_forces_table(name='design forces 2', all_uls=True)

bridge_ref.dc_ratio_table()
bridge_ref.cost_table()

fig = bridge_ref.plot_effects('Cable_Loss', 'Moment', label='Cable loss ranges', c=colors[0])
fig = bridge_ref.plot_effects('Cable_Loss_4', 'Moment', fig=fig, label='4. cable loss', c=colors[1])
adjust_effects_plots(fig)

fig = bridge_ref.plot_effects('Strength-I', 'Moment', label='Fatigue', c=colors[0])
fig = bridge_ref.plot_effects('Fatigue', 'Moment', fig=fig, label='Fatigue', c=colors[0])
adjust_effects_plots(fig)
fig.savefig('hanger forces.png')


# Save the demand over capacity ratios of the reference case
dc = []
for cs in bridge_ref.cost_cross_sections:
    dc.append(cs.dc_max)
f = open('dc_ratios.pckl', 'wb')
pickle.dump(dc, f)
f.close()

# Save the bridge file
f = open('bridge.pckl', 'wb')
pickle.dump(bridge_ref, f)
f.close()

# Show memory usage
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
tracemalloc.stop()
