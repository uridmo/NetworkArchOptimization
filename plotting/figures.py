from matplotlib import pyplot


def initialize_plot_structure(fig_size=(4, 1.5), dpi=240):
    fig = pyplot.figure(figsize=fig_size, dpi=dpi)
    ax = fig.add_subplot(111)
    return fig, ax


def initialize_plot_internal_force():
    return


