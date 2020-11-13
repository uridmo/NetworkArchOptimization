import os


def save_plot(fig, directory, name):
    if not os.path.isdir(directory):
        os.makedirs(directory)
    fig.savefig(directory+'/'+name+'png')
    return
