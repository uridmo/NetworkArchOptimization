import pickle
import numpy as np
from matplotlib import pyplot

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.adjustments import adjust_plot
from plotting.plots import make_plots, arch_or_tie_plots
from plotting.general import colors
from plotting.tables import dc_overview_table

# Import the base case
f = open('../base case/bridge.pckl', 'rb')
bridge_ref = pickle.load(f)
f.close()
cable_loss = False
for n in [13,26]:
    bridge_thrust = BlennerhassettBridge(n_hangers=n, n_cross_girders=n, cable_loss=cable_loss)

    print('Potential for permanent moment distribution optimisation (n=' + str(n) + ')')
    for cs in bridge_thrust.cost_cross_sections[0:3]:
        name = cs.dc_max_limit_state
        m_max = cs.effects[name]['Moment'][0]
        m_min = cs.effects[name]['Moment'][1]
        m_dif = abs(m_max+m_min)/2
        dc_dif = 8/9 * m_dif / cs.moment_z_resistance
        print([m_max, m_min, m_dif, dc_dif])

    bridge_polynomial = BlennerhassettBridge(curve_fitting='Polynomial-n', n_hangers=n, n_cross_girders=n, cable_loss=cable_loss)
    bridge_spline = BlennerhassettBridge(curve_fitting='Spline-n', n_hangers=n, n_cross_girders=n, cable_loss=cable_loss)
    bridge_continuous = BlennerhassettBridge(arch_shape='Continuous optimisation', arch_optimisation=False, n_hangers=n, n_cross_girders=n, cable_loss=cable_loss)

    bridges_dict = {'Thrust line arch': bridge_thrust,
                    'Polynomial approximation': bridge_polynomial,
                    'Spline approximation': bridge_spline,
                    'Continuous approximation': bridge_continuous}
    load_groups = {'permanent state_'+str(n): 'Permanent',
                   'strength-I_'+str(n): 'Strength-I'}

    # make_plots(bridges_dict, load_groups, lw=0.8, big_plots=True)
    arch_or_tie_plots(bridges_dict, load_groups, lw=0.8)

    bridge_thrust.dc_ratio_table(name='dc_table_'+str(n))
    dc_overview_table('dc_comparison_'+str(n), bridges_dict, slice_cs=slice(0, 3))

    span = 267.8
    rise = 53.5
    radius = (rise ** 2 + (span / 2) ** 2) / (2 * rise)
    fig, axs = pyplot.subplots(1, 2, figsize=(8, 2), dpi=240)
    for i, key in enumerate(bridges_dict):
        bridge = bridges_dict[key]
        nodes = bridge.network_arch.arch.nodes
        x = np.array([node.x for node in nodes])
        y = np.array([node.y for node in nodes])
        y_ref = [rise * (1 - ((x_i - span / 2) / (span / 2)) ** 2) for x_i in x]
        axs[0].plot(x, y-y_ref, label=key, c=colors[i], lw=0.7)

    y = np.array([rise - radius * (1 - (1 - ((x_i - span / 2) / radius) ** 2) ** 0.5) for x_i in x])
    axs[0].plot(x, y-y_ref, label='Circular arch', c=colors[i+1], lw=0.7)

    axs[0].set_title('Arch shape')
    axs[0].set_ylabel('Deviation [m]')
    adjust_plot(axs[0], step=0.2, min_0=True)

    axs[1].remove()
    handles, labels = axs[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.55, 0.85), frameon=False)
    fig.savefig('arch_shapes_'+str(n)+'.png')
    pyplot.show()
