import numpy as np


        
def showOrientation(model, ax):
    nodes = model['Nodes']['Location']
    elements = model['Beams']['Nodes']
    
    for i in range(len(elements)):
        start, end = elements[i][0], elements[i][1]
        
        xm=(nodes[start][0]+nodes[end][0])/2
        ym=(nodes[start][1]+nodes[end][1])/2
        
        
        dx=(nodes[end][0]-nodes[start][0])
        dy=(nodes[end][1]-nodes[start][1])
        
        Vec=[dx, dy]
        Vec = Vec/np.linalg.norm(Vec)
        normalVec= [dy, -dx]
        normalVec = normalVec/np.linalg.norm(normalVec)
        
        x1=[xm+0.15*normalVec[0]-0.3*Vec[0],   xm+0.15*normalVec[0]-0.15*Vec[0]]
        x2=[xm+0.15*normalVec[0]-0.075*Vec[0], xm+0.15*normalVec[0]+0.075*Vec[0]]
        x3=[xm+0.15*normalVec[0]+0.15*Vec[0],  xm+0.15*normalVec[0]+0.3*Vec[0]]
        y1=[ym+0.15*normalVec[1]-0.3*Vec[1],   ym+0.15*normalVec[1]-0.15*Vec[1]]
        y2=[ym+0.15*normalVec[1]-0.075*Vec[1], ym+0.15*normalVec[1]+0.075*Vec[1]]
        y3=[ym+0.15*normalVec[1]+0.15*Vec[1],  ym+0.15*normalVec[1]+0.3*Vec[1]]
        
        ax.plot(x1,y1, color='black', lineWidth=1)#, dashes=[3, 1.5]
        ax.plot(x2,y2, color='black', lineWidth=1)
        ax.plot(x3,y3, color='black', lineWidth=1)