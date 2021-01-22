import numpy as np
from matplotlib import pyplot

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.adjustments import adjust_plot
from plotting.plots import arch_or_tie_plots
from plotting.general import colors

cable_loss = False
arch_shape = 'Continuous optimisation'
span = 267.8
rise = 53.5

b_table = np.zeros((5, 7))
dif_table = np.zeros((5, 7))
for i, a_mid in enumerate([85, 75, 65, 55, 45]):
    for j, a_1 in enumerate([105, 95, 85, 75, 65, 55, 45]):
        if a_1 < a_mid or a_1 >= 2 * a_mid:
            continue
        bridge = BlennerhassettBridge(arch_optimisation=False, arch_shape=arch_shape, cable_loss=cable_loss,
                                      hanger_arrangement='Constant Change',
                                      hanger_params=(np.radians(a_1), np.radians(a_mid)),
                                      curve_fitting='Polynomial')
        b_table[i, j] = bridge.network_arch.arch.b
        dif_table[i, j] = bridge.network_arch.arch.d
np.savetxt("b_values.csv", b_table, delimiter=', ', fmt='%2.3f', newline=' \\\\\n')
np.savetxt("dif_values.csv", dif_table, delimiter=', ', fmt='%2.3f', newline=' \\\\\n')

b_2_table = np.zeros((1, 8))
dif_2_table = np.zeros((1, 8))
for i, b in enumerate([5, 10, 15, 20, 25, 30, 35, 40]):
    bridge = BlennerhassettBridge(arch_optimisation=False, arch_shape=arch_shape, cable_loss=cable_loss,
                                  hanger_arrangement='Radial', hanger_params=(np.radians(b),),
                                  curve_fitting='Polynomial')
    b_2_table[0, i] = bridge.network_arch.arch.b
    dif_2_table[0, i] = bridge.network_arch.arch.d
np.savetxt("b_values_2.csv", b_2_table, delimiter=', ', fmt='%2.3f', newline=' \\\\\n')
np.savetxt("dif_values_2.csv", dif_2_table, delimiter=', ', fmt='%2.3f', newline=' \\\\\n')

