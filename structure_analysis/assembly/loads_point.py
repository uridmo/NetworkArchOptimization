# -*- coding: utf-8 -*-
"""
Created on Tue May 14 07:05:08 2019

@author: umorf

The module contains the function to assemble point loads. It provides the result
in a special format which will be used to create the force matrix and to 
calculate the internal forces.
"""

import numpy as np

from .rotation_matrix import get_rotation_matrix
from .shape_functions import *


def assemble_point_loads(nodes_lists, elements_lists, beams_information,
                         point_loads):
    """Assembles the global point loads into nodal forces.
    
    It uses the separately defined shape functions to determine the equivalent
    nodal forces.
    
    If a point load is exactly on an element node, the program assumed half
    of the forces to come from each side. In this case the assembled_forces will
    be appended with two lists, since two elements are involved.
    
    Arguments:
        nodes_lists       -- a list containing for each beam an ordered list of
                             the node numbers along the beam
        elements_lists    -- a list containing for each beam a list of the 
                             elements on the beam in consecutive order
        beams_information -- a list containing for each beam its main information:
                             beam length, beam orientation, number of elements 
                             created on the beam, length of these elements
        point_loads       -- a list containing the point loads of a loadgroup
    
    Return values:
        assembled_forces -- a list containing for an assembled load its element
                            number, the two node numbers, the orientation and
                            its nodal forces
    """
    
    assembled_forces = []
    
    #Expand the assembled forces list for each point load.
    for point_load in point_loads:
        
        #Get beam information
        beam_nr = point_load[0]
        theta   = beams_information[beam_nr][1]
        r       = get_rotation_matrix(theta)
        
        #Find the position on the element x, the elements length, its node
        #numbers and the element it is on.     
        element_length = beams_information[beam_nr][3]

        x = point_load[1] % element_length
        j = int(point_load[1] // element_length)

        #Special Case Handling: Load is at the end of the beam
        if j == beams_information[beam_nr][2]:
            j-= 1
            x = beams_information[beam_nr][3]
        
        element_nr  = elements_lists[beam_nr][j]
        nodenr1     = nodes_lists[beam_nr][j]
        nodenr2     = nodes_lists[beam_nr][j+1]
                
        #Rotate into local System
        global_force = np.array(point_load[2:5]).reshape((3,1))
        localpointloads = r[0:3,0:3].transpose() @ global_force
        
        Fx = localpointloads[0][0]
        Fy = localpointloads[1][0]
        Mz = localpointloads[2][0]
        
        #Calculation of local Nodal Forces
        Fx1 = n1(x,element_length)*Fx
        Fy1 = n3(x,element_length)*Fy + n31(x,element_length)*Mz    
        Mz1 = n4(x,element_length)*Fy + n41(x,element_length)*Mz    
        Fx2 = n2(x,element_length)*Fx    
        Fy2 = n5(x,element_length)*Fy + n51(x,element_length)*Mz    
        Mz2 = n6(x,element_length)*Fy + n61(x,element_length)*Mz
        
        localnodalforces=np.array([[Fx1], [Fy1], [Mz1], [Fx2], [Fy2], [Mz2]])
        
        #Append the assembled forces. (Which also includes the important element information)
        #Normal Case: Load is not on a node. (Only if it is on the last node it
        # does not need special treatment)
        if x!=0 or j==0:
            assembled_forces.append([element_nr, nodenr1, nodenr2, theta, localnodalforces])
            
        #Special Case Handling: Load is exactly on a node (x == 0).
        else:
            zeros = np.zeros((3,1))
            
            # The load will always have been assumed to be on the later element.
            # Therefore the forces calculated on the second element node are
            # always zero in this special case.
            assembled_forces.append([element_nr, nodenr1, -1, theta,
                                     np.vstack((localnodalforces[0:3]/2, zeros))]),
            assembled_forces.append([elements_lists[beam_nr][j-1], -1, nodenr1, theta,
                                     np.vstack((zeros, localnodalforces[0:3]/2))])

    return assembled_forces