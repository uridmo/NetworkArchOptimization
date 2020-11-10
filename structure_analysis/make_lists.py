# -*- coding: utf-8 -*-
"""
Created on Fri May  3 17:06:58 2019

@author: umorf
"""
"""
This module contains the functions which create the output dictionaries from
the displacement and internal force matrices.
"""

import numpy as np
 
def get_dictionaries(discretization_information, internal_displacements_matrices,
                     internal_forces_matrices):
    """Creates two lists containing the components of interst for each loadgroup.
    
    The first list contains the displacements in each degree of freedom. The 
    second list contains the internal forces.
    
    Arguments:
        discretization_information      -- the dictionary containing the 
                                           information of the discretized system
        internal_displacements_matrices -- the matrices storing the elementwise
                                           displacements (left and right) of 
                                           each loadgroup
        internal_forces_matrices        -- the matrices storing the elementwise
                                           internal forces (left and right) of 
                                           each loadgroup
        
    Return values:
        displacement_dictionaries    -- the dictionary containing the 
                                        displacements of the system
        internal_forces_dictionaries -- the dictionary containing the internal 
                                        forces of the system
    """
    elements_lists = discretization_information['Elements']
    amount_of_loadgroups = len(internal_displacements_matrices)
    
    keys_id=['Displacement X','Displacement Y','Rotation Z']
    keys_if=['Normal Force','Shear Force','Moment']
    
    displacement_dictionaries=[]
    internal_forces_dictionaries=[]
    
    #Append the lists with a dictionary for each loadgroup.
    for i in range(amount_of_loadgroups):
        
        #Get the displacements and the internal forces of the current loagroup
        id_matrix = internal_displacements_matrices[i]
        if_matrix = np.asarray(internal_forces_matrices[i])
        
        #Create the Displacement Dictionary
        displacements_dict = create_dictionary(elements_lists, id_matrix, keys_id)
        internal_forces_dict = create_dictionary(elements_lists, if_matrix, keys_if)

        displacement_dictionaries.append(displacements_dict)
        internal_forces_dictionaries.append(internal_forces_dict)
        
    return displacement_dictionaries, internal_forces_dictionaries

 
def create_dictionary(elements_lists, internal_matrix, keys):
    """Creates a dictionary with the 3 entries of an internal matrix.
    
    Arguments:
        elements_lists  -- a list containing for each beam a list of the elements
                           on the beam in consecutive order
        internal_matrix -- any internal matrix (storing left and right side
                           values) to be saved in a dictionary
        keys            -- the keys to the three entries of the dictionary
        
    Return values:
        dictionary -- the dictionary created from the internal_matrix
    """
    value_1 = []
    value_2 = []
    value_3 = []
    
    #Append the lists for each beam.
    for element_list in elements_lists:
        
        #Get the left and the right element number of each beam.
        left_element  = element_list[0]
        right_element = element_list[-1]
        
        #Get a value for each node. Combine the left values with the last right value.
        values_left = internal_matrix[0:3,left_element:right_element+1]
        value_right = internal_matrix[3:6,right_element].reshape((3,1))
        values_beam = np.hstack((values_left,value_right))
        
        value_1.append(list(values_beam[0,:]))
        value_2.append(list(values_beam[1,:]))
        value_3.append(list(values_beam[2,:]))
    
    dictionary = {keys[0]: value_1, keys[1]: value_2, keys[2]:value_3}
    
    return dictionary