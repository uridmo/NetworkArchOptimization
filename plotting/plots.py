from matplotlib import pyplot

from plotting.adjustments import adjust_overview_plots, adjust_effects_plots, adjust_plot
from plotting.general import colors
from PIL import Image


def crop_plots(name, plot_size, i_figure, legend_size, legend_top_anchor,
               legend_width=600, i_skip_title=(), i_skip_label=()):
    im = Image.open(name+'.png')
    new_image = Image.new('RGB', (max(plot_size[0] * 960, legend_top_anchor[0] + legend_width*legend_size[0]),
                                  max(plot_size[1] * 480, legend_top_anchor[1] + 51*legend_size[1])),
                                  (255, 255, 255))
    cropped_figures = [im.crop((0, 0, 960, 480)),
                       im.crop((960, 0, 1920, 480)),
                       im.crop((1920, 0, 2880, 480)),
                       im.crop((0, 480, 960, 960)),
                       im.crop((960, 480, 1920, 960))]
    legend_fig= im.crop((1920, 480, 2880, 960))
    legends = []
    for i in range(legend_size[0]*legend_size[1]):
        legends.append(legend_fig.crop((122, 65+i*51, 122+legend_width, 65+(i+1)*51)))
    n = -1
    for j in range(plot_size[1]):
        for i in range(plot_size[0]):
            n += 1
            if n > len(i_figure)-1:
                continue
            i_fig = i_figure[n]
            fig = cropped_figures[i_fig]
            if i_fig in i_skip_title:
                im_new = Image.new('RGB', (760, 80), (255, 255, 255))
                fig.paste(im_new, (200, 0))
            if i_fig in i_skip_label:
                im_new = Image.new('RGB', (80, 480), (255, 255, 255))
                fig.paste(im_new, (0, 0))
            new_image.paste(fig, (i*960, j*480))
    n = -1
    for j in range(legend_size[0]):
        for i in range(legend_size[1]):
            n += 1
            legend = legends[n]
            new_image.paste(legend, (legend_top_anchor[0] + j * legend_width,
                                     legend_top_anchor[1] + i * 51))
    new_image.save(name+'_plot'+".png", "PNG")
    return


def make_plots(bridges_dict, load_groups, dc=True, big_plots=False, all_labels=False, quantity='Moment', lw=1.0, ls='-', marker='x'):

    for name in load_groups:
        load_group = load_groups[name]
        fig = None
        for i, key in enumerate(bridges_dict):
            label = key
            bridge = bridges_dict[key]
            if big_plots:
                fig = bridge.plot_all_effects(load_group, fig=fig, dc=dc, label=label, c=colors[i], lw=lw, ls=ls, marker=marker)
            else:
                fig = bridge.plot_effects(load_group, quantity, fig=fig, dc=dc, label=label, c=colors[i], lw=lw, ls=ls, marker=marker)

        if big_plots:
            adjust_overview_plots(fig, all_labels, dc=dc)
        else:
            adjust_effects_plots(fig, quantity, dc=dc)

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

