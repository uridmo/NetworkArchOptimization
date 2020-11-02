import matplotlib.pyplot as plt

def plotLegend(ax):   
    """
    Adds the legend with required settings to the plot.
    """
    
    ax.legend(frameon=False, loc='center left', bbox_to_anchor=(1, 0.5))

    return

def plotTitle(fig, title):
    """
    Adds the title with required settings to the plot.
    """

    fig.suptitle(title, x=0.5, y=0.9, fontsize=18, fontweight='bold',va='bottom', ha='center')
    
    return

def initializePlot():
    """
    Initializes the figure for the plots.
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)    
    plt.gca().set_aspect('equal', adjustable='box')
    plt.margins(0.1,0.1)
     
    return(fig, ax)

def adjustPlot(ax):
    """
    Adjust the margin between structure and axis.
    """
    
    ax.axis('tight')    

    ax.axis('scaled')
    xmin, xmax, ymin, ymax = ax.axis()
    if (xmax-xmin)>4*(ymax-ymin):
        dif=(xmax-xmin)-4*(ymax-ymin)
        
        ax.set_ylim(ymin-dif/2,ymax+dif/2)
    if (ymax-ymin)>4*(xmax-xmin):
        dif=(ymax-ymin)-4*(xmax-xmin)
        ax.set_xlim(xmin-dif/2,xmax+dif/2)
    
    #    ax.set_xlim(xmin-1, xmax+1)
#    ax.set_ylim(ymin-1, ymax+1)


    return
    