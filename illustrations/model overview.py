import numpy as np
from matplotlib import pyplot
from matplotlib.markers import MarkerStyle

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.save import save_plot

hanger_params = (np.radians(63),)
bridge_parallel = BlennerhassettBridge(hanger_params=hanger_params)

fig, ax = bridge_parallel.plot_elements()
span = 267.8 + 50
rise = 53.5 + 17
n = 100
x_arch = list(np.linspace(0, span, 2 * n + 1))
x_arch = x_arch[9:-9]
y_arch = [rise * (1 - ((x - span / 2) / (span / 2)) ** 2) for x in x_arch]
x_arch = [x - 25 for x in x_arch]
ax.plot(x_arch, y_arch, color='black', linewidth=1)
ax.plot([0, 267.8], [-20, -20], color='black', linewidth=1)

cs_tie_x = [0, 6.2, 34.8, 92.13, 267.8-92.13, 267.8-34.8, 267.8-6.2, 267.8]
cs_tie_y = [-20]*8
ax.plot(cs_tie_x, cs_tie_y, "|", color='black')

cs_arch_x = [0-11, 3.8-8, 28.8-5, 83.91]
cs_arch_x += [267.8 - x for x in cs_arch_x[::-1]]

rotations = [40, 37, 30, 20]
rotations += [-r for r in rotations[::-1]]

for i, x in enumerate(cs_arch_x):
    x+=25
    y = rise * (1 - ((x - span / 2) / (span / 2)) ** 2)
    x-=25
    m = MarkerStyle("|")
    m._transform.rotate_deg(rotations[i])
    ax.plot(x, y, marker=m, color='black')

ax.text(-20, -40, "Tie 0", rotation=None, fontsize=8)
ax.text(10, -40, "Tie 1", rotation=None, fontsize=8)
ax.text(50, -40, "Tie 2", rotation=None, fontsize=8)
ax.text(122, -40, "Tie 3", rotation=None, fontsize=8)
ax.text(195, -40, "Tie 2", rotation=None, fontsize=8)
ax.text(236, -40, "Tie 1", rotation=None, fontsize=8)
ax.text(264, -40, "Tie 0", rotation=None, fontsize=8)

ax.text(-40, 2, "Arch 0", rotation=40, fontsize=8)
ax.text(-11, 25, "Arch 1", rotation=34, fontsize=8)
ax.text(35, 53, "Arch 2", rotation=24, fontsize=8)
ax.text(120, 77, "Arch 3", rotation=None, fontsize=8)
ax.text(204, 51, "Arch 2", rotation=-24, fontsize=8)
ax.text(250, 23, "Arch 1", rotation=-34, fontsize=8)
ax.text(280, 0, "Arch 0", rotation=-40, fontsize=8)
pyplot.show()
save_plot(fig, 'model overview', 'segments')
