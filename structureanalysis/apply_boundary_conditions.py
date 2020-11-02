# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 13:48:51 2019

@author: umorf

The module contains the functions which are used to split the stiffness and the
force matrix into unrestricted and restricted components.
"""

import numpy as np
import scipy.sparse as sps

  
def apply_boundary_conditions(boundary_conditions, stiffness_matrix, force_matrix):
    """Splits the stiffness and the force matrices according to the boundary conditions.
    
    Arguments:
        boundary_conditions -- the boundary conditions of the system
        stiffness_matrix    -- the stiffness matrix of the system, not including
                               restricted degrees
        force_matrix        -- a matrix combining the global force vectors of 
                               the different loadgroups
        
    Return values:
        stiffness_and_force_matrices -- the stiffness and force matrices of the
                                        restricted and the unrestricted nodal
                                        directions
    """
    restricted_degrees  = boundary_conditions['Restricted Degrees']
    size                = stiffness_matrix.shape[0]

    # Determine the nodal directions which are restricted.    
    indices_todelete = get_indices_todelete(restricted_degrees)
    
    #Get the matrices that can delete certain rows or columns
    (delete_rows, delete_columns,
     keep_rows, keep_columns) = modifier_matrices(size, indices_todelete)
    
    #Delete the determined nodes with the help of the modifier matrices.
    force_matrix_modified     = delete_rows @ force_matrix
    force_matrix_supports     = keep_rows   @ force_matrix
    stiffness_matrix_modified = delete_rows @ stiffness_matrix @ delete_columns
    stiffness_matrix_supports = keep_rows   @ stiffness_matrix @ delete_columns
    
    stiffness_and_force_matrices=[stiffness_matrix_modified,
                                  stiffness_matrix_supports,
                                  force_matrix_modified,
                                  force_matrix_supports]
    
    return stiffness_and_force_matrices
 
def modifier_matrices(original_size, indices):
    """Creates matrices that can keep or delete certain indices from a square matrix.
    
    It creates the four matrices to delete or extract the specified indices
    (rows or columns).
    
    Keyword argument:
        original_size -- the original amount of indices
        indices       -- a numpy vector of the indices which are to be kept or 
                         deleted
        
    Return values:
        delete_rows    -- a matrix which deletes the specified indices rows
                          from a matrix with original_size rows
        delete_columns -- a matrix which deletes the specified indices columns
                          from a matrix with original_size columns
        keep_rows      -- a matrix which extracts the specified indices rows
                          from a matrix with original_size rows
        keep_columns   -- a matrix which extracts the specified indices columns
                          from a matrix with original_size columns
    """
    amount_todelete = indices.shape[0]
    new_size        = original_size-amount_todelete
    
    #List of the elements which are to be kept or killed
    elements_original = np.arange(original_size)
    elements_keep     = np.delete(elements_original, indices,None)
    elements_kill     = indices
    
    #List of ones for each element to kill or keep
    ones_kill = np.ones(new_size)
    ones_keep = np.ones(amount_todelete)
    
    #Normal Count for the elements to kill or keep
    count_kill = np.arange(new_size)
    count_keep = np.arange(amount_todelete)
    
    #Create the sparse matrices to delete or keep the specified rows or cols.
    delete_rows    = sps.csr_matrix((ones_kill,(count_kill,elements_keep)),
                                    (new_size,original_size))
    
    delete_columns = sps.csr_matrix((ones_kill,(elements_keep,count_kill)),
                                    (original_size,new_size))
    
    keep_rows      = sps.csr_matrix((ones_keep,(count_keep,elements_kill)),
                                    (amount_todelete,original_size))
    
    keep_columns   = sps.csr_matrix((ones_keep,(elements_kill,count_keep)),
                                    (original_size,amount_todelete))

    return delete_rows, delete_columns, keep_rows, keep_columns

 
def get_indices_todelete(restricted_degrees):
    """Gives a numpy vector of the nodal degrees of freedom which are to be deleted.
    
    Arguments:
        restricted_degrees -- the restricted degrees of the system 
    
    Return values:
        indices_todelete -- a numpy vector containing all the nodal degrees of
                            freedom which are to be deleted
    """
    indices_todelete=np.empty((1,0),dtype=int)
    
    #Append the list for each restricted nodal degree of freedom
    for restricted_degree in restricted_degrees:
        if restricted_degree[1]==1:
            indices_todelete=np.append(indices_todelete,restricted_degree[0]*3+0)
            
        if restricted_degree[2]==1:
            indices_todelete=np.append(indices_todelete,restricted_degree[0]*3+1)
            
        if restricted_degree[3]==1:
            indices_todelete=np.append(indices_todelete,restricted_degree[0]*3+2)
    
    return indices_todelete