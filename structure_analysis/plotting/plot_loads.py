import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, FancyArrow

from .plotHinges import plotHinges
from .plotSettings import plotTitle, initialize_plot, adjustPlot
from .plotStructure import plotStructure
from .plotSupports import plot_supports
from .showOrientation import showOrientation


def plot_loads(model, load_group, title, save_plot=False):
    """
    Takes the structure and load dictionary.
    
    Displays the structure with the user defined loads
    
    TO DO: display of forced rotations
    """
    # Settings    
    # ------------------------------------
    forceColor = 'red'
    displacementColor = 'green'
    MomentColor = 'blue'
    # ------------------------------------

    try:
        nodalLoads = model['Loads'][load_group]['Nodal']
    except:
        nodalLoads = []

    try:
        pointLoads = model['Loads'][load_group]['Point']
    except:
        pointLoads = []

    try:
        lineLoads = model['Loads'][load_group]['Distributed']
    except:
        lineLoads = []

    try:
        functionLoads = model['Loads'][load_group]['Functions']
    except:
        functionLoads = []

    try:
        displacements = model['Loads'][load_group]['Initial Displacements']
    except:
        displacements = []

    elements = model['Beams']['Nodes']
    nodes = model['Nodes']['Location']

    # Determine Scaling Factors
    # ------------------------------------

    x_min = min([node[0] for node in nodes])
    x_max = max([node[0] for node in nodes])
    z_min = min([node[1] for node in nodes])
    z_max = max([node[1] for node in nodes])
    length = (((x_max - x_min) ** 2 + (z_max - z_min) ** 2) ** 0.5)

    scaleDisplacements = 20
    max_nodal = max([max(abs(nodalload[1]), abs(nodalload[2])) for nodalload in nodalLoads] + [0])
    max_point = max([max(abs(pointload[2]), abs(pointload[3])) for pointload in pointLoads] + [0])
    max_force = max(max_point, max_nodal, 0.0001)
    max_length = length / 6
    min_length = length / 24

    max_distributed = max([max(abs(lineload[3]), abs(lineload[6]),
                               abs(lineload[4]), abs(lineload[7]),
                               abs(lineload[5]), abs(lineload[8])) for lineload in lineLoads] + [0])
    values_functions = []
    for functionload in functionLoads:
        for i in range(3):
            if functionload[3 + i] != 0 and functionload[3 + i] != None:
                values_functions.extend([abs(functionload[3 + i](x)) for x in np.linspace(functionload[1],
                                                                                          functionload[2],
                                                                                          num=15)])
    max_functional = max(values_functions + [0])
    scaleDistributedForces = length / 8 / max(max_distributed, max_functional, 0.0001)
    # ------------------------------------

    # Set up the plot
    fig, ax = initialize_plot()
    plotTitle(fig, 'Structure and Loads')
    plotStructure(model, ax)
    showOrientation(model, ax)
    plot_supports(model, ax)
    if 'Releases' in model['Beams']:
        plotHinges(model, ax)

    # Add identifiers for legend
    ax.plot(0, 0, color=displacementColor, label=f'Forced Displacement (scaled by factor {scaleDisplacements})')
    ax.plot(0, 0, color=forceColor, label='Force')
    ax.plot(0, 0, color=MomentColor, label='Moment')

    # Cycle through nodal Forces
    for i in range(len(nodalLoads)):
        Fx = np.sign(nodalLoads[i][1]) * max(abs(nodalLoads[i][1]) / max_force * max_length, min_length)
        Fy = np.sign(nodalLoads[i][2]) * max(abs(nodalLoads[i][2]) / max_force * max_length, min_length)
        Mz = nodalLoads[i][3]

        if (abs(Fx) + abs(Fy)) > 0:
            targetX = nodes[nodalLoads[i][0]][0]
            targetY = nodes[nodalLoads[i][0]][1]
            arrow = FancyArrow(targetX - Fx, targetY - Fy, Fx, Fy, length_includes_head=True,
                               head_width=3, linewidth=2, color=forceColor, zorder=10)
            ax.add_patch(arrow)
        if Mz != 0:
            targetX = nodes[nodalLoads[i][0]][0]
            targetY = nodes[nodalLoads[i][0]][1]
            #            ax.plot(targetX,targetY, marker='o', markersize=4, alpha=1, color=MomentColor)

            if Mz > 0:
                arc = Arc([targetX, targetY], 1, 1, 0, 240, 110, linewidth=2, color=MomentColor, zorder=5)
                ax.add_patch(arc)
                arrow = FancyArrow(targetX - 0.35255, targetY + 0.35405, -0.01, -0.005, length_includes_head=True,
                                   head_width=3, linewidth=0.5, color=MomentColor, zorder=5)
            else:
                arc = Arc([targetX, targetY], 1, 1, 0, 70, 300, linewidth=2, color=MomentColor, zorder=5)
                ax.add_patch(arc)
                arrow = FancyArrow(targetX + 0.35255, targetY + 0.35405, +0.01, -0.005, length_includes_head=True,
                                   head_width=3, linewidth=0.5, color=MomentColor, zorder=5)
            ax.add_patch(arrow)

    # Cycle through elements
    for i in range(len(elements)):
        elementVector = [nodes[elements[i][1]][0] - nodes[elements[i][0]][0],
                         nodes[elements[i][1]][1] - nodes[elements[i][0]][1]]
        elementVector = elementVector / np.linalg.norm(elementVector)

        # Plot point loads
        for j in range(len(pointLoads)):
            if int(pointLoads[j][0]) == i:
                loc = pointLoads[j][1]
                Fx = pointLoads[j][2] * scaleForces
                Fy = pointLoads[j][3] * scaleForces
                Mz = pointLoads[j][4]

                # Prevent error of arrow without length
                if (abs(Fx) + abs(Fy)) > 0:
                    targetX = nodes[elements[i][0]][0] + elementVector[0] * loc
                    targetY = nodes[elements[i][0]][1] + elementVector[1] * loc

                    arrow = FancyArrow(targetX - Fx, targetY - Fy, Fx, Fy, length_includes_head=True, head_width=4,
                                       linewidth=2, color=forceColor, zorder=10)
                    ax.add_patch(arrow)
                if Mz != 0:
                    targetX = nodes[elements[i][0]][0] + elementVector[0] * loc
                    targetY = nodes[elements[i][0]][1] + elementVector[1] * loc
                    ax.plot(targetX, targetY, marker='o', markersize=4, alpha=1, color=MomentColor)

                    if Mz > 0:
                        arc = Arc([targetX, targetY], 1, 1, 0, 240, 110, linewidth=2, color=MomentColor, zorder=5)
                        ax.add_patch(arc)
                        arrow = FancyArrow(targetX - 0.35255, targetY + 0.35405, -0.01, -0.005,
                                           length_includes_head=True,
                                           head_width=0.2, linewidth=0.5, color=MomentColor, zorder=5)
                    else:
                        arc = Arc([targetX, targetY], 1, 1, 0, 70, 300, linewidth=2, color=MomentColor, zorder=5)
                        ax.add_patch(arc)
                        arrow = FancyArrow(targetX + 0.35255, targetY + 0.35405, +0.01, -0.005,
                                           length_includes_head=True,
                                           head_width=0.2, linewidth=0.5, color=MomentColor, zorder=5)
                    ax.add_patch(arrow)

        # Plot line loads
        for j in range(len(lineLoads)):
            if int(lineLoads[j][0]) == i:
                lStart = lineLoads[j][1]
                lEnd = lineLoads[j][2]
                qxStart = lineLoads[j][3] * scaleDistributedForces
                qyStart = lineLoads[j][4] * scaleDistributedForces
                mzStart = lineLoads[j][5] * scaleDistributedForces

                qxEnd = lineLoads[j][6] * scaleDistributedForces
                qyEnd = lineLoads[j][7] * scaleDistributedForces
                mzEnd = lineLoads[j][8] * scaleDistributedForces

                if qxStart != 0 or qyStart != 0 or qxEnd != 0 or qyEnd != 0:
                    targetXStart = nodes[elements[i][0]][0] + elementVector[0] * lStart
                    targetXEnd = nodes[elements[i][0]][0] + elementVector[0] * lEnd
                    targetYStart = nodes[elements[i][0]][1] + elementVector[1] * lStart
                    targetYEnd = nodes[elements[i][0]][1] + elementVector[1] * lEnd

                    x = [targetXEnd - qxEnd, targetXStart - qxStart]
                    y = [targetYEnd - qyEnd, targetYStart - qyStart]
                    ax.plot(x, y, color=forceColor, linewidth=1.3)

                    # draw Arrows
                    amount = int((lEnd - lStart) / (length / 20) + 2)
                    for k in range(amount):
                        l = lStart + (lEnd - lStart) * k / (amount - 1)
                        x = nodes[elements[i][0]][0] + elementVector[0] * l
                        y = nodes[elements[i][0]][1] + elementVector[1] * l
                        arrowlengthx = (lEnd - l) / (lEnd - lStart) * qxStart + (l - lStart) / (lEnd - lStart) * qxEnd
                        arrowlengthy = (lEnd - l) / (lEnd - lStart) * qyStart + (l - lStart) / (lEnd - lStart) * qyEnd
                        if abs(arrowlengthx) > length / 100 or abs(arrowlengthy) > length / 100:
                            arrow = FancyArrow(x - arrowlengthx, y - arrowlengthy, arrowlengthx, arrowlengthy,
                                               length_includes_head=True,
                                               head_width=4, linewidth=1, color=forceColor, zorder=5)
                            ax.add_patch(arrow)

                if mzStart != 0 or mzEnd != 0:
                    targetXStart = nodes[elements[i][0]][0] + elementVector[0] * lStart
                    targetXEnd = nodes[elements[i][0]][0] + elementVector[0] * lEnd
                    targetYStart = nodes[elements[i][0]][1] + elementVector[1] * lStart
                    targetYEnd = nodes[elements[i][0]][1] + elementVector[1] * lEnd

                    x = [targetXEnd - elementVector[1] * mzEnd, targetXStart - elementVector[1] * mzStart]
                    y = [targetYEnd + elementVector[0] * mzEnd, targetYStart + elementVector[0] * mzStart]
                    ax.plot(x, y, color=MomentColor, lineWidth=1.3)

                    # draw Lines
                    amount = int((lEnd - lStart) / (length / 20) + 2)
                    for k in range(amount):
                        l = lStart + (lEnd - lStart) * k / (amount - 1)
                        x = nodes[elements[i][0]][0] + elementVector[0] * l
                        y = nodes[elements[i][0]][1] + elementVector[1] * l
                        arrowlengthx = -elementVector[1] * (
                                    (lEnd - l) / (lEnd - lStart) * mzStart + (l - lStart) / (lEnd - lStart) * mzEnd)
                        arrowlengthy = elementVector[0] * (
                                    (lEnd - l) / (lEnd - lStart) * mzStart + (l - lStart) / (lEnd - lStart) * mzEnd)
                        if abs(arrowlengthx) > length / 100 or abs(arrowlengthy) > length / 100:
                            ax.plot([x, x + arrowlengthx], [y, y + arrowlengthy], color=MomentColor, lineWidth=1)

        # Plot forced displacements
        for j in range(len(displacements)):
            if int(displacements[j][0]) == i:
                if (abs(displacements[j][1] + abs(displacements[j][2]) > 0)):
                    arrow = FancyArrow(nodes[int(displacements[j][0])][0], nodes[int(displacements[j][0])][1],
                                       scaleDisplacements * displacements[j][1],
                                       scaleDisplacements * displacements[j][2],
                                       length_includes_head=True, head_width=0.2, linewidth=2, color=displacementColor)
                    ax.add_patch(arrow)

                if displacements[j][3] != 0:
                    targetX = nodes[displacements[i][0]][0]
                    targetY = nodes[displacements[i][0]][1]
                    ax.plot(targetX, targetY, marker='o', markersize=4, alpha=1, color=displacementColor)
                    arc = Arc([targetX, targetY], 1, 1, 0, 240, 120, linewidth=2, color=displacementColor, zorder=5)
                    ax.add_patch(arc)
                    if displacements[j][3] > 0:
                        arrow = FancyArrow(targetX - 0.35255, targetY + 0.35405, -0.01, -0.005,
                                           length_includes_head=True,
                                           head_width=0.2, linewidth=0.5, color=displacementColor, zorder=5)
                    else:
                        arrow = FancyArrow(targetX - 0.35255, targetY - 0.35405, -0.01, +0.005,
                                           length_includes_head=True,
                                           head_width=0.2, linewidth=0.5, color=displacementColor, zorder=5)
                    ax.add_patch(arrow)

        for j in range(len(functionLoads)):
            if int(functionLoads[j][0]) == i:

                lStart = functionLoads[j][1]
                lEnd = functionLoads[j][2]

                qx = functionLoads[j][3]
                qy = functionLoads[j][4]
                mz = functionLoads[j][5]

                if (qx != 0 and qx != None) or (qy != 0 and qy != None):
                    targetXStart = nodes[elements[i][0]][0] + elementVector[0] * lStart
                    targetXEnd = nodes[elements[i][0]][0] + elementVector[0] * lEnd
                    targetYStart = nodes[elements[i][0]][1] + elementVector[1] * lStart
                    targetYEnd = nodes[elements[i][0]][1] + elementVector[1] * lEnd

                    x1 = []
                    y1 = []

                    # draw Arrows
                    amount = int((lEnd - lStart) / (length / 20) + 2)
                    for k in range(amount * 4 - 3):
                        l = lStart + (lEnd - lStart) * k / (((4 * amount - 3)) - 1)
                        x = nodes[elements[i][0]][0] + elementVector[0] * l
                        y = nodes[elements[i][0]][1] + elementVector[1] * l
                        arrowlengthx = 0
                        arrowlengthy = 0
                        if (qx != 0 and qx != None):
                            arrowlengthx += qx(l) * scaleDistributedForces
                        if (qy != 0 and qy != None):
                            arrowlengthy += qy(l) * scaleDistributedForces

                        if ((abs(arrowlengthx) > length / 100 or abs(arrowlengthy) > length / 100)
                                and k % 4 == 0):
                            arrow = FancyArrow(x - arrowlengthx, y - arrowlengthy, arrowlengthx, arrowlengthy,
                                               length_includes_head=True,
                                               head_width=0.13, linewidth=1, color=forceColor, zorder=5)
                            ax.add_patch(arrow)
                        x1.append(x - arrowlengthx)
                        y1.append(y - arrowlengthy)
                    ax.plot(x1, y1, color=forceColor, lineWidth=1.3)

                if (mz != 0 and mz != None):
                    targetXStart = nodes[elements[i][0]][0] + elementVector[0] * lStart
                    targetXEnd = nodes[elements[i][0]][0] + elementVector[0] * lEnd
                    targetYStart = nodes[elements[i][0]][1] + elementVector[1] * lStart
                    targetYEnd = nodes[elements[i][0]][1] + elementVector[1] * lEnd

                    x1 = []
                    y1 = []

                    # draw Lines
                    amount = int((lEnd - lStart) / (length / 20) + 2)
                    for k in range(amount * 4 - 3):
                        l = lStart + (lEnd - lStart) * k / (((4 * amount - 3)) - 1)
                        x = nodes[elements[i][0]][0] + elementVector[0] * l
                        y = nodes[elements[i][0]][1] + elementVector[1] * l
                        arrowlengthx = -elementVector[1] * mz(l)
                        arrowlengthy = elementVector[0] * mz(l)
                        if ((abs(arrowlengthx) > length / 100 or abs(arrowlengthy) > length / 100)
                                and k % 4 == 0):
                            ax.plot([x, x + arrowlengthx], [y, y + arrowlengthy], color=MomentColor, lineWidth=1)
                        x1.append(x + arrowlengthx)
                        y1.append(y + arrowlengthy)
                    ax.plot(x1, y1, color=MomentColor, lineWidth=1.3)

    #plotLegend(ax)
    adjustPlot(ax)
    # plt.show()

    if save_plot:
        if not os.path.isdir('Plots ' + title):
            os.makedirs('Plots ' + title)
        plt.savefig('Plots ' + title + '/Loadgroup ' + str(load_group) + '_Forces.png', dpi=300, bbox_inches='tight')

    return ax
