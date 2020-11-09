import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
from .plotHinges import plotHinges
from .plotStructure import plotStructure
from .plotSupports import plot_supports
from .plotSettings import plotLegend, plotTitle, initialize_plot, adjustPlot
import os


def plot_internal_forces(model, displacements, internal_forces, load_group, quantity, title, show_extrema=False,
                         save_plot=False, scale_max=0.25):
    """
    Takes the structure and the reactions and plots the structure with the 
    required quantity of forces or deformations.

    quantity: value from ['M', 'V', 'N', 'uh', 'uv', 'deformedShape']. If 'deformedShape is
    selected, the horizontal and vertical deformations are combined to show the deformed
    Shape of the structure         
    
    scaleMax: Displayed size of the maximum value is this factor multiplyied with 
    the shortest element length.  
    
    Sign convention: If the length of the element is larger in x than y, positive 
    values are displayed in positive y-direction. If the length is larger in y than x,
    positive values are displayed in positive y-direction.
    """
    # Settings    
    # ------------------------------------
    forceColor = 'orange'  # Color used if forces are shown
    displacementColor = 'green'  # Color used if displacements are shown
    maxColor = 'red'  # Color used for max values
    minColor = 'blue'  # Color used for min values

    #    # Title of the diagram
    #    title = {'M': 'Bending Moments', 'V': 'Shear Forces', 'N': 'Normal Forces',
    #             'uh': 'Horizontal Displacements', 'uv': 'Vertical Displacements'}
    # ------------------------------------

    # Abbreviations
    nodes = model['Nodes']['Location']
    elements = model['Beams']['Nodes']
    numPoints = [len(sublist) for sublist in displacements[0]['Displacement X']]

    x_min = min([node[0] for node in nodes])
    x_max = max([node[0] for node in nodes])
    z_min = min([node[1] for node in nodes])
    z_max = max([node[1] for node in nodes])
    diag_length = (((x_max - x_min) ** 2 + (z_max - z_min) ** 2) ** 0.5)

    if quantity == 'Deformed Shape':
        reactions = {'uh': displacements[load_group]['Displacement X'],
                     'uv': displacements[load_group]['Displacement Y']}
        uh_max = max(max(sublist) for sublist in reactions['uh'])
        uh_min = min(min(sublist) for sublist in reactions['uh'])
        uv_max = max(max(sublist) for sublist in reactions['uv'])
        uv_min = min(min(sublist) for sublist in reactions['uv'])
        uh_amax = max(uh_max, -uh_min)
        uv_amax = max(uv_max, -uv_min)
        umax = (((uh_amax) ** 2 + (uv_amax) ** 2) ** 0.5)

        scaleDisplacements = diag_length / 8 / max(umax, 0.0001)
        exp = np.floor(np.log10(scaleDisplacements))
        l = np.round(scaleDisplacements / (10 ** exp))
        scaleDisplacements = l * 10 ** exp

    else:
        if quantity in ['Normal Force', 'Shear Force', 'Moment']:
            reaction = internal_forces[load_group][quantity]
        elif quantity in ['Displacement X', 'Displacement Y', 'Rotation Z']:
            reaction = displacements[load_group][quantity]

        reaction_max = [max(max(sublist), -min(sublist)) for sublist in reaction]

        if max(reaction_max) > 1e-6:
            scaleForces = diag_length / 12 / max(reaction_max)
        else:
            scaleForces = 0

    # Definitions of colors, units, and scaling factor for legend
    if quantity in ['Normal Force', 'Shear Force']:
        myColor = forceColor
        currentUnit = 'kN'
        unitScale = 1
    elif quantity == 'Moment':
        myColor = forceColor
        currentUnit = 'kNm'
        unitScale = 1
    elif quantity in ['Displacement X', 'Displacement Y', 'Deformed Shape']:
        myColor = displacementColor
        currentUnit = 'mm'
        unitScale = 1e3
    elif quantity == 'Rotation Z':
        myColor = displacementColor
        currentUnit = 'mrad'
        unitScale = 1e3
    else:
        print('Chosen quantity not defined. Choose M,V,N,uh,uv,deformedShape')
        return

    # Begin the plot
    fig, ax = initialize_plot()

    # Cycle through elements
    for i in range(len(elements)):
        start, end = elements[i][0], elements[i][1]
        x = np.linspace(nodes[start][0], nodes[end][0], numPoints[i])
        y = np.linspace(nodes[start][1], nodes[end][1], numPoints[i])

        # Plot the combined x- and y-displacements if required
        if quantity == 'Deformed Shape':
            if i == 0:
                plotStructure(model, ax)  # Plot structure only at first loop
                ax.plot(0, 0, color=displacementColor, dashes=(2, 3), label='qualitative displacements')
                plotTitle(fig, f'Deformations (scaled by factor {scaleDisplacements:.1f})')

            ValuesHorizontal = np.array(reactions['uh'][i]) * scaleDisplacements
            ValuesVertical = np.array(reactions['uv'][i]) * scaleDisplacements

            ax.plot(x + ValuesHorizontal, y + ValuesVertical, color=displacementColor, dashes=(2, 3))


        # Plot single quantities
        else:
            if i == 0:
                # Plot structure overlapping    
                plotStructure(model, ax)
                plotTitle(fig, quantity)

                # Add the identifier for pos/neg values to the legend
                ax.plot(0, 0, color=maxColor, label=quantity)
            values = np.array(reaction[i])

            # Construct unit vector perpendicular to the corresponding element accoring to 
            # sign convention
            dx = (nodes[end][0] - nodes[start][0])
            dy = (nodes[end][1] - nodes[start][1])

            normalVec = [dy, -dx]
            #            if lengthX[i] > lengthY[i]:
            #                if nodes[start][0] <= nodes[end][0]:
            #                    normalVec = [-(nodes[end][1]-nodes[start][1]), (nodes[end][0]-nodes[start][0])]
            #                else:
            #                    normalVec = [-(nodes[start][1]-nodes[end][1]), (nodes[start][0]-nodes[end][0])]
            #            elif lengthX[i] <= lengthY[i]:
            #                if nodes[start][1] <= nodes[end][1]:
            #                    normalVec = [(nodes[end][1]-nodes[start][1]), -(nodes[end][0]-nodes[start][0])]
            #                else:
            #                    normalVec = [(nodes[start][1]-nodes[end][1]), -(nodes[start][0]-nodes[end][0])]

            normalVec = normalVec / np.linalg.norm(normalVec)

            # absolute coordinates for displaying the values
            xmax = x + normalVec[0] * scaleForces * values
            ymax = y + normalVec[1] * scaleForces * values

            # Plot the upper and lower bound
            ax.plot(xmax, ymax, color=maxColor, alpha=0.4)
            #            ax.plot(xmin, ymin, color=minColor, alpha=0.4)

            # fill between max and min
            fillCoordinates = np.zeros((numPoints[i] + 2, 2))
            fillCoordinates[numPoints[i]] = np.array([nodes[end][0], nodes[end][1]])
            fillCoordinates[numPoints[i] + 1] = np.array([nodes[start][0], nodes[start][1]])

            for j in range(numPoints[i]):
                fillCoordinates[j][0] = xmax[j]
                fillCoordinates[j][1] = ymax[j]

            polygon = Polygon(fillCoordinates, edgecolor=None, fill=True, facecolor=myColor, alpha=0.5)
            ax.add_patch(polygon)

            # Show the extrema in plot and legend
            if show_extrema:
                maxIndex, minIndex = np.argmax(values), np.argmin(values)
                maxX, maxY = xmax[maxIndex], ymax[maxIndex]
                minX, minY = xmax[minIndex], ymax[minIndex]

                # Show maxima and minima with element 'title' in legend
                ax.plot(0, 0, linestyle='None', label=r'$\bf{Element}$' + ' ' + r'$\bf{%i:}$' % i)
                ax.plot(maxX, maxY, color=maxColor, marker='.', markersize=10, linestyle='None',
                        label=f'Max {quantity}={values[maxIndex] * unitScale:.1f} {currentUnit} at ({x[maxIndex]:.2f}, {y[maxIndex]:.2f}) m')
                ax.plot(minX, minY, color=minColor, marker='.', markersize=10, linestyle='None',
                        label=f'Min {quantity}={values[minIndex] * unitScale:.1f} {currentUnit} at ({x[minIndex]:.2f}, {y[minIndex]:.2f}) m')

    # plotLegend(ax)
    plotHinges(model, ax)
    plot_supports(model, ax)
    adjustPlot(ax)
    plt.show()

    if save_plot:

        if not os.path.isdir('Plots ' + title):
            os.makedirs('Plots ' + title)

        plt.savefig('Plots ' + title + '/Loadgroup ' + str(load_group) + '_' + quantity + '.png', dpi=300,
                    bbox_inches='tight')
