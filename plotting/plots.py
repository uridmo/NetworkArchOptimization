from matplotlib import pyplot

from plotting.adjustments import adjust_overview_plots, adjust_effects_plots
from plotting.general import colors
from plotting.save import save_plot


def make_plots(bridges_dict, load_groups, folder, big_plots=False, show=True):

    for name in load_groups:
        load_group = load_groups[name]
        fig = None
        for i, key in enumerate(bridges_dict):
            label = key
            bridge = bridges_dict[key]
            if big_plots:
                fig = bridge.plot_all_effects(load_group, fig=fig, label=label, c=colors[i])
            else:
                fig = bridge.plot_effects(load_group, 'Moment', fig=fig, label=label, c=colors[i])

        if big_plots:
            adjust_overview_plots(fig)
        else:
            adjust_effects_plots(fig)

        save_plot(fig, folder, name)

        if show:
            pyplot.show()
    return
