from matplotlib import pyplot

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.adjustments import adjust_plot
from plotting.general import colors

bridge = BlennerhassettBridge(arch_optimisation=False, n_floor_beams=100)

span = 267.8
F = 296
c = 1 #1/(40.5*100*2)*1000

x = [(i+1)/(101)*span for i in range(100)]
f_2 = []
f_6 = []
f_10 = []
for i in range(100):
    d_2 = bridge.network_arch.hangers.effects['F'+str(i+1)]['Normal Force'][1]
    d_6 = bridge.network_arch.hangers.effects['F'+str(i+1)]['Normal Force'][5]
    d_10 = bridge.network_arch.hangers.effects['F'+str(i+1)]['Normal Force'][9]
    f_2.append(F*d_2*c)
    f_6.append(F*d_6*c)
    f_10.append(F*d_10*c)

span = 267.8
rise = 53.5
fig, axs = pyplot.subplots(1, 2, figsize=(8, 2), dpi=240)

axs[0].plot(x, f_2, label='2. Hanger', c=colors[0], lw=1)
axs[0].plot(x, f_6, label='6. Hanger', c=colors[1], lw=1)
axs[0].plot(x, f_10, label='10. Hanger', c=colors[2], lw=1)

# axs[0].set_title('Fatigue limit state')
axs[0].set_ylabel('Hanger force [kN]')
axs[0].set_xlabel('Design truck position [m]')
adjust_plot(axs[0], step=100, min_0=True)

axs[1].remove()
handles, labels = axs[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.55, 0.85), frameon=False)
fig.savefig('figures/fatigue.png')
pyplot.show()
