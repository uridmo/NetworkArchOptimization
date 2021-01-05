from matplotlib import pyplot

from plotting.adjustments import adjust_overview_plots, adjust_effects_plots, adjust_plot
from plotting.general import colors


def make_plots(bridges_dict, load_groups, big_plots=False, lw=1.0, ls='-', marker='x'):

    for name in load_groups:
        load_group = load_groups[name]
        fig = None
        for i, key in enumerate(bridges_dict):
            label = key
            bridge = bridges_dict[key]
            if big_plots:
                fig = bridge.plot_all_effects(load_group, fig=fig, label=label, c=colors[i], lw=lw, ls=ls, marker=marker)
            else:
                fig = bridge.plot_effects(load_group, 'Moment', fig=fig, label=label, c=colors[i], lw=lw, ls=ls, marker=marker)

        if big_plots:
            adjust_overview_plots(fig)
        else:
            adjust_effects_plots(fig)

        fig.savefig(name + ".png")
        pyplot.show()
    return


def arch_or_tie_plots(bridges_dict, load_groups, lw=1.0, ls='-', arch=True, effect='Moment'):

    for name in load_groups:
        load_group = load_groups[name]
        fig, axs = pyplot.subplots(1, 2, figsize=(8, 2), dpi=240)
        for i, key in enumerate(bridges_dict):
            label = key
            bridge = bridges_dict[key]
            if arch:
                bridge.network_arch.arch.plot_effects(axs[0], load_group, effect, label=label, c=colors[i], lw=lw, ls=ls)
            else:
                bridge.network_arch.tie.plot_effects(axs[0], load_group, effect, label=label, c=colors[i], lw=lw, ls=ls)

        if arch:
            axs[0].set_title('Arch')
        else:
            axs[0].set_title('Tie')

        axs[0].set_ylabel('M [MNm]')
        adjust_plot(axs[0])

        axs[1].remove()
        handles, labels = axs[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.55, 0.85), frameon=False)
        fig.savefig(name + ".png")
        pyplot.show()
    return

