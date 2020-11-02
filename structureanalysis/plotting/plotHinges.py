import matplotlib.pyplot as plt

def plotHinges(model, ax):
    """
    Takes the structure and the figure to plot on.
    
    structure['hinges'] is an array with rows [elementNumber, stateStartNode, stateEndNode],
    where the state of a node is 1 (hinged connection) or 0 (clamped connection).
    
    Plots the hinges as white circles with black edge.
    """
    hinges = model['Beams']['Releases']
    nodes = model['Nodes']['Location']
    beams = model['Beams']['Nodes']
    
    for i in range(len(hinges)):
        startNode     = beams[hinges[i][0]][0]
        endNode       = beams[hinges[i][0]][1]
        
        if hinges[i][1] == 1:
            x,y = nodes[startNode][0], nodes[startNode][1]  
            ax.plot(x,y, marker='o', markersize=8, alpha=1, color='black')
            ax.plot(x,y, marker='o', markersize=5, alpha=1, color='white')                

        if hinges[i][2] == 1:
            x,y = nodes[endNode][0], nodes[endNode][1]                  
            ax.plot(x,y, marker='o', markersize=8, alpha=1, color='black')
            ax.plot(x,y, marker='o', markersize=5, alpha=1, color='white')                
