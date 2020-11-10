# -*- coding: utf-8 -*-
"""
Created on Tue May 21 12:55:30 2019

@author: umorf

The module contains the function which modifies the force matrix to take into
account initial displacements.
"""

import numpy as np

def apply_initial_displacements(loads, stiffness_matrix, force_matrix):
    """Adds the forces corresponding to the initial displacements in the force matrix.
    
    Arguments:
        loads            -- a list containing the loadgroups of the model
        stiffness_matrix -- the stiffness matrix of the system, not including 
                            restricted degrees 
        force_matrix     -- a matrix combining the global force vectors of the
                            different loadgroups 
    """
    #Creates a displacement matrix including all initial displacements.
    nodal_dofs = stiffness_matrix.shape[0]
    displacement_matrix = np.zeros((nodal_dofs, len(loads)))
    
    #Build the initial displacement matrix.
    for load_nr, loadgroup in enumerate(loads,0):
        
        if ('Initial Displacements' in loadgroup 
            and loadgroup['Initial Displacements']):
            
            for initial_displacement in loadgroup['Initial Displacements']:
                
                nr = initial_displacement[0]
                
                displacement_matrix[nr*3:nr*3+3, load_nr] += initial_displacement[1:4]
    
    #Deduct the forces corresponding to the initial dispalcement from the 
    #force matrix.        
    force_matrix -= (stiffness_matrix @ displacement_matrix)
      
    return