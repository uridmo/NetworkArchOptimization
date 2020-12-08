from matplotlib import pyplot

from plotting.loads import plot_loads
from plotting.supports import plot_supports_new


def plot_model(model, elements, fig_size=(4, 1.5), title='', i=0, show=True):
    fig = pyplot.figure(figsize=fig_size, dpi=480)
    ax = fig.add_subplot(111)
    if title:
        fig.suptitle(title, x=0.5, y=0.8, fontsize=16, fontweight='bold',
                     va='bottom', ha='center')
    pyplot.gca().set_aspect('equal', adjustable='box')
    pyplot.axis('off')
    pyplot.margins(0.1, 0.1)
    elements.plot_elements(ax)
    plot_supports_new(model, ax)
    if i is not None:
        plot_loads(model, i, ax)
    if show:
        pyplot.show()
    return fig, ax
