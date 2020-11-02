import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon



def plotSupports(model, ax):
    """
    Takes the structure and the figure to plot on.
    
    structure['boundaryConditions'] is a matrix with columns [nodeNumber, x-translation, y-translation, rotation].
    Each movement is either restricted (1) or free (1)
    
    Plots the supports.
    """
    bc = model['Boundary Conditions']['Restricted Degrees']
    nodes = model['Nodes']['Location']
    
    # Dimensions of the structure
    x_max=max(node[0] for node in nodes)
    x_min=min(node[0] for node in nodes)
    y_max=max(node[1] for node in nodes)
    y_min=min(node[1] for node in nodes)
    dimX, dimY = x_max-x_min, y_max-y_min
    
    supportSize = (max(dimX, dimY/2)+max(dimX/2, dimY))*0.04
    for i in range(len(bc)):
        # x and y coord. of current node
        x,y = nodes[bc[i][0]][0], nodes[bc[i][0]][1]
        
        # Supports for restricted rotation
        if bc[i][3] == 1:
            d = 0.3*supportSize
            solidPolygon = Polygon([[x+d,y+d],[x-d,y+d],[x-d,y-d],[x+d,y-d]],
                                    fill=True, color='black', alpha=1)
            ax.add_patch(solidPolygon)
            if bc[i][1] == 1 and bc[i][2] == 1:
                hatchedPolygon = Polygon([[x-2*d, y-d], [x+2*d, y-d], [x+2*d, y-2*d],[x-2*d, y-2*d]],
                                         fill=False, hatch='//////',edgecolor=None)
                ax.add_patch(hatchedPolygon)
            if bc[i][1] == 1 and bc[i][2] == 0:
                ax.plot([x-2*d, x+2*d], [y-d,y-d], color='black')
                ax.plot([x-2*d, x+2*d], [y-2*d,y-2*d], color='black')

            if bc[i][1] == 0 and bc[i][2] == 1:
                ax.plot([x-d, x-d], [y-2*d,y+2*d], color='black')
                ax.plot([x-2*d, x-2*d], [y-2*d,y+2*d], color='black')
        
        # Supports for free rotation (Pin supports)
        if bc[i][3] == 0:           
            if bc[i][1] == 1:
                support = Polygon([[x,y],
                                   [x-np.sqrt(3)/2*supportSize,y-0.5*supportSize],
                                   [x-np.sqrt(3)/2*supportSize, y+0.5*supportSize]],
                                    fill=False, edgecolor='black')
                ax.add_patch(support)
                ax.plot([x-1.1*supportSize, x-1.1*supportSize], [y-0.5*supportSize, y+0.5*supportSize], color='black')
                
            if bc[i][2] == 1:
                support = Polygon([[x,y],
                                   [x+0.5*supportSize, y-np.sqrt(3)/2*supportSize],
                                   [x-0.5*supportSize, y-np.sqrt(3)/2*supportSize]],
                                    fill=False, edgecolor='black')
                ax.add_patch(support)
                ax.plot([x-0.5*supportSize, x+0.5*supportSize], [y-1.1*supportSize, y-1.1*supportSize], color='black')

