import numpy as np


def plotStructure(model, ax):
    elements = model['Beams']['Nodes']
    nodes = model['Nodes']['Location']
    
    for i in range(len(elements)):
        start, end = elements[i][0], elements[i][1]
        x = np.linspace(nodes[start][0], nodes[end][0])
        y = np.linspace(nodes[start][1], nodes[end][1])
        ax.plot(x, y, color='black', linewidth=2)
    return
