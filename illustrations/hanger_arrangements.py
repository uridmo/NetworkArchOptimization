import numpy as np

from bridges.Blennerhassett import BlennerhassettBridge


# bridge_parallel = BlennerhassettBridge(hanger_params=(np.radians(65),),
#                                        arch_optimisation=False)
# fig, ax = bridge_parallel.plot_elements()
# fig.savefig('figures/arrangements_parallel.png')
#
# bridge_constant_change = BlennerhassettBridge(hanger_arrangement='Constant Change',
#                                               hanger_params=(np.radians(95), np.radians(65)),
#                                               arch_optimisation=False)
# fig, ax = bridge_constant_change.plot_elements()
# fig.savefig('figures/arrangements_constant_change.png')
#
#
# bridge_radial = BlennerhassettBridge(hanger_arrangement='Radial',
#                                      hanger_params=(np.radians(25),),
#                                      arch_optimisation=False)
# fig, ax = bridge_radial.plot_elements()
# fig.savefig('figures/arrangements_radial.png')

bridge_vertical = BlennerhassettBridge(hanger_params=(np.radians(89.9),),
                                       arch_optimisation=False, n_hangers=20)
fig, ax = bridge_vertical.plot_elements()
fig.savefig('figures/arrangements_vertical.png')

