from descartes import PolygonPatch
import pickle
from plotting.general import colors

from matplotlib import pyplot

f = open('web.pckl', 'rb')
poly_web = pickle.load(f)
poly_web_y = poly_web[0]
poly_web_u = poly_web[1]
poly_web_y_2 = poly_web[2]

f = open('top.pckl', 'rb')
poly_top = pickle.load(f)
poly_top_y = poly_top[0]
poly_top_u = poly_top[1]
poly_top_y_2 = poly_top[2]

f = open('bot.pckl', 'rb')
poly_bot = pickle.load(f)
poly_bot_y = poly_bot[0]
poly_bot_u = poly_bot[1]
poly_bot_y_2 = poly_bot[2]

sol_y = poly_web_y.intersection(poly_top_y.intersection(poly_bot_y))
sol_u = poly_web_u.intersection(poly_top_u.intersection(poly_bot_u))
sol_y_2 = poly_web_y_2.intersection(poly_top_y_2.intersection(poly_bot_y_2))


# def plot_coords(ax, ob):
#     x, y = ob.xy
#     ax.plot(x, y, '+', color='grey')
#     return

fig = pyplot.figure(dpi=720)
ax = fig.add_subplot(111)

# plot_coords(ax, sol.exterior)
patch = PolygonPatch(sol_y, facecolor=colors[2], edgecolor=colors[2], alpha=0.5)
ax.add_patch(patch)
patch = PolygonPatch(sol_u, facecolor=colors[1], edgecolor=colors[1], alpha=0.5)
ax.add_patch(patch)
patch = PolygonPatch(sol_y_2, facecolor=colors[0], edgecolor=colors[0], alpha=0.5)
ax.add_patch(patch)
ax.set_xlim([-120, 120])
ax.set_ylim([-70, 70])
pyplot.show()
