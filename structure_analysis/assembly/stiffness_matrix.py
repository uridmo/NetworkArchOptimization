# -*- coding: utf-8 -*-
"""
Created on Mon May 13 21:24:07 2019

@author: umorf

The module contains the function to assemble the sparse stiffness matrix.
"""

import numpy as np
import scipy.sparse as sps

from .local_stiffness_matrix import get_local_stiffness_matrix
from .local_stiffness_matrix import include_releases
from .rotation_matrix import get_rotation_matrix


def get_stiffness_matrix(beams_stiffness, nodes_lists, releases_beams, 
                         beams_information):
    """Assembles the sparse stiffness matrix of an unrestricted system.
    
    In a first step the function creates the lists needed to build the sparse
    stiffness matrix which is assembled in a second step.
    
    Arguments:
        beams_stiffness   -- a list of each beams normal, beding (and shear) 
                             stiffnesses 
        nodes_lists       -- a list containing for each beam an ordered list of
                             the node numbers along the beam 
        releases_beams    -- a dictionary saving the special releases to the 
                             corresponding beam number a dictionary containing 
                             all the model's information on the beams 
        beams_information -- a list containing for each beams main information:
                             beam length, beam orientation, number of elements 
                             created on the beam, length of these elements 
    
    Return values:
        stiffness_matrix -- the stiffness matrix of the system, not including 
                            restricted degrees 
    """
    #Create the lists to create the sparse stiffness matrix
    data = []
    col  = []
    row  = []    
    
    #Expand the lists for each beam
    for i in range(len(nodes_lists)):
        #Get the beams element length and rotation matrix.
        length  = beams_information[i][3]
        theta   = beams_information[i][1]
        r       = get_rotation_matrix(theta)
                
        #Calculate the global stiffness matrix of the beams elements. (They are
        #the same withhin the same beam.)
        k_local = get_local_stiffness_matrix(length, beams_stiffness[i])
        k_global= r @ k_local @ r.transpose()
        
        
        #Expand the lists for each element on the beam.
        kglobalaslist=np.reshape(k_global, 36).tolist()
        for j in range(beams_information[i][2]):
            startnode=nodes_lists[i][j]
            endnode=nodes_lists[i][j+1]
            
            #Expand the columns and the rows list with the corresponding 36 entries.
            row.extend([3*startnode]*6+[3*startnode+1]*6+[3*startnode+2]*6
                       +[3*endnode]*6+[3*endnode+1]*6+[3*endnode+2]*6)
            col.extend([3*startnode, 3*startnode+1, 3*startnode+2,
                        3*endnode, 3*endnode+1, 3*endnode+2]*6)
            
            #Expand the data list with the elements stiffness matrix.
            #Normal treatment for the element withhin the beam.
            if j!=0 and j!=beams_information[i][2]-1:
                data.extend(kglobalaslist)
            
            #Special Treatment for the first and the last element on a beam.
            else:
                #Check for hinges:
                if j==0:
                    left_release=releases_beams.get(i, [0,0])[0]
                else:
                    left_release=0
                if j==beams_information[i][2]-1:
                    right_release=releases_beams.get(i, [0,0])[1]
                else:
                    right_release=0
                
                #Adapt the stiffness matrix to the releases.
                k_with_releases = include_releases(k_global, left_release,
                                                   right_release)
                
                k_with_releases_aslist = np.reshape(k_with_releases,36).tolist()
                data.extend(k_with_releases_aslist)
            
        
    #Build the sparse stiffness matrix.
    number_of_nodes = max([max(sublist)] for sublist in nodes_lists)[0] + 1

    stiffness_matrix=sps.csr_matrix((data, (row, col)), shape=(3*number_of_nodes,
                                                               3*number_of_nodes))

    return stiffness_matrix