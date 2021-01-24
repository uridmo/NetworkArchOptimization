import numpy as np

from bridges.Blennerhassett import BlennerhassettBridge

hanger_params = np.array([102,  70, 107,  65,  91,  43, 128,  67,  99,  46,  60,  96,  47])
hanger_params = np.array([113,  65, 123,  65, 123,  28, 105, 100,  93,  94,  80,  84,  47])
hanger_params = np.array([ 96,  99,  52, 101, 117,  58,  46,  81, 122,  42,  91,  64,  40])
bridge = BlennerhassettBridge(hanger_arrangement='Unpatterned',
                              hanger_params=hanger_params,
                              self_stress_state='Zero-displacement',
                              curve_fitting='Polynomial')

fig, ax = bridge.plot_elements()
fig.savefig('optimised design_3.png')
bridge.dc_ratio_table()

