from matplotlib import pyplot


def adjust_overview_plots(fig):
    axs = fig.get_axes()

    axs[0].set_title('Arch')
    axs[0].set_xlim([0, 270])
    axs[0].set_ylabel('N [MN]')
    adjust_plot(axs[0])

    axs[1].set_title('Tie')
    axs[1].set_xlim([0, 270])
    adjust_plot(axs[1])

    axs[2].set_title('Hangers')
    axs[2].set_xlim([0, 270])
    axs[2].set_ylabel('D/C [-]')
    axs[2].set_ylim(bottom=0)
    adjust_plot(axs[2])
    axs[2].set_ylim([0, 1])

    axs[3].set_xlim([0, 270])
    axs[3].set_ylabel('M [MNm]')
    adjust_plot(axs[3])

    axs[4].set_xlim([0, 270])
    adjust_plot(axs[4])

    axs[5].remove()
    handles, labels = axs[4].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.7, 0.45), frameon=False)
    pyplot.show()
    return


def adjust_small_plots(fig):
    axs = fig.get_axes()

    axs[0].set_title('Arch')
    axs[0].set_xlim([0, 270])
    axs[0].set_ylabel('M [MNm]')
    adjust_plot(axs[0])

    axs[1].set_title('Tie')
    axs[1].set_xlim([0, 270])
    adjust_plot(axs[1])

    axs[2].set_title('Hangers')
    axs[2].set_xlim([0, 270])
    axs[2].set_ylabel('D/C [-]')

    adjust_plot(axs[2])

    axs[3].remove()
    handles, labels = axs[1].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.55, 0.45), frameon=False)

    pyplot.show()
    return


def adjust_plot(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    y_ticks = ax.get_yticks()
    ax.set_ylim([y_ticks[0], y_ticks[-1]])
    ax.set_yticks(y_ticks)
    ax.axhline(0, color='black', lw=0.5)
    return
