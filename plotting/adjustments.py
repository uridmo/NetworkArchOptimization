from matplotlib import pyplot


def adjust_overview_plots(fig):
    axs = fig.get_axes()

    axs[0].set_title('Arch')
    axs[0].set_xlim([0, 270])
    adjust_plot(axs[0])

    axs[1].set_title('Tie')
    axs[1].set_xlim([0, 270])
    adjust_plot(axs[1])

    axs[2].set_title('Hangers')
    axs[2].set_xlim([0, 270])
    adjust_plot(axs[2])

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