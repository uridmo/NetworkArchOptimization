# -*- coding: utf-8 -*-
"""
Created on Sat Apr 27 07:45:09 2019

@author: umorf

The module contains all functions used to calculate the internal forces from
the displacements and for combining them with the internal forces from 
assembling.
"""

import numpy as np

from .assembly.local_stiffness_matrix import get_local_stiffness_matrix
from .assembly.local_stiffness_matrix import include_releases
from .assembly.rotation_matrix import get_rotation_matrix


def get_internal_forces(beams, displacement_matrix, internal_forces_assembly,
                        discretization_information):
    """Calculates the internal forces from the displacements and combines them with the ones from assembling.
    
    First the nodal displacements of each element are extracted from the
    displacement matrix. They are saved into a new matrix per loadgroup with
    one column per element. This allows the fast calculation of the internal 
    forces of all elements on a beam in one second step.
    
    Arguments:
        beams                      -- a dictionary containing all the model's
                                      information on the beams
        displacement_matrix        -- the matrix containing the displacement 
                                      vectors for each loadgroup
        internal_forces_assembly   -- a list of matrices saving the internal 
                                      forces for each loadgroup resulting from 
                                      assembling its loads
        discretization_information -- the dictionary containing the information
                                      of the discretized system
        
    Return values:
        internal_forces_matrices -- the matrices storing the elementwise 
                                    internal forces (left and right) of each 
                                    loadgroup
    """
    nodes_lists         = discretization_information['Nodes']
    beams_information   = discretization_information['Beams Information']
    elements_lists      = discretization_information['Elements']
    releases            = discretization_information['Releases']
    beams_stiffness     = beams['Stiffness']
    
    internal_displacements_matrices = get_internal_displacements(nodes_lists,
                                                                 elements_lists,
                                                                 displacement_matrix)
    
    #Calulate the internal forces of the nodal displacements.
    internal_forces_matrices = calculate_internal_forces(internal_displacements_matrices,
                                                         elements_lists, releases,
                                                         beams_information,
                                                         beams_stiffness)
    
    #Subtract the internal forces from assembling the model.
    for i in range(len(internal_forces_matrices)):
        internal_forces_matrices[i] -= internal_forces_assembly[i]
        
    
    return internal_displacements_matrices, internal_forces_matrices

 
def get_internal_displacements(nodes_lists, elements_lists, displacement_matrix):
    """Saves the displacements of each element into a column, each loadgroup into a matrix.
    
    Arguments:
        nodes_lists         -- a list containing for each beam an ordered list 
                               of the node numbers along the beam
        elements_lists      -- a list containing for each beam a list of the 
                               elements on the beam in consecutive order
        displacement_matrix -- the matrix containing the displacement vectors 
                               for each loadgroup
        
    Return values:
        internal_displacements -- a list with a matrix for each loadgroup, 
                                  which contains the internal forces for each 
                                  element a list of dictionaries containing for
                                  each loadgroup the displacements of all beams
                                  nodes
    """
    
    internal_displacements = []
    amount_of_elements = elements_lists[-1][-1]+1
    amount_of_loadgroups = displacement_matrix.shape[1]
    d_mat = displacement_matrix
    
    #Append the internal displacements for each loadgroup.
    for k in range(amount_of_loadgroups):
        
        internal_displacements_loadgroup = np.empty((6,amount_of_elements))
        id_loadgroup = internal_displacements_loadgroup
        
        for beam_nr, element_list in enumerate(elements_lists, 0):
            for j_element, element_number in enumerate(element_list, 0):
                #Get node and element numbers.
                nr1=nodes_lists[beam_nr][j_element]
                nr2=nodes_lists[beam_nr][j_element+1]
                el_nr=element_number
                
                #Define the corresponding internal displacements
                id_loadgroup[:,el_nr]=np.hstack([d_mat[3*nr1:3*nr1+3, k],
                                                 d_mat[3*nr2:3*nr2+3, k]])
        internal_displacements.append(id_loadgroup)

    return internal_displacements

 
def calculate_internal_forces(internal_displacements, elements_lists, releases,
                              beams_information, beams_stiffness):
    """Calculates the internal forces of each loadgroup into a matrix.
    
    Per matrix, each column corresponds to one element.
    
    Arguments:
        internal_displacements -- a list with a matrix for each loadgroup,
                                  which contains the internal forces for each 
                                  element a list of dictionaries containing for
                                  each loadgroup the displacements of all beams
                                  nodes
        elements_lists         -- a list containing for each beam a list of the
                                  elements on the beam in consecutive order
        releases               -- a dictionary with the keys 'Beams' and 
                                  'Elements' containing for each a dictionary 
                                  containing the hinged releases to the 
                                  according element or beam numbers
        beams_information      -- a list containing for each beam its main 
                                  information: beam length, beam orientation,
                                  number of elements created on the beam, 
                                  length of these elements
        beams_stiffness        -- a list of each beams normal, beding (and 
                                  shear) stiffnesses
        
    Return values:
        internal_forces_displacements -- the internal forces resulting from the
                                         displacements (without internal forces
                                         from assembling)
    """
    internal_forces_displacements = []
    amount_of_elements            = elements_lists[-1][-1]+1
    amount_of_loadgroups          = len(internal_displacements)
    signmatrix                    = np.diag(np.array([-1,1,-1,1,-1,1]))
    i_d                           = internal_displacements
    
    #Append the internal forces (from displacements) for each loadgroup.
    for k in range(amount_of_loadgroups):
        
        internal_forces_loadgroup = np.empty((6,amount_of_elements))
        if_loadgroup              = internal_forces_loadgroup
        
        #Handle every beam.
        for beam_nr, element_list in enumerate(elements_lists, 0):
            
            length = beams_information[beam_nr][3]
            klocal = get_local_stiffness_matrix(length, beams_stiffness[beam_nr])
            r      = get_rotation_matrix(beams_information[beam_nr][1])
            r_t    = r.transpose() 
            
            #Get the first and the last element and their realases.
            first_element = element_list[0]
            last_element  = element_list[-1]
            f_e           = first_element
            l_e           = last_element
            f_e_releases  = releases['Elements'].get(f_e,[0,0])
            l_e_releases  = releases['Elements'].get(l_e,[0,0])
            
            #Calculate the internal forces for all elements on the beam.
            if_loadgroup[:,f_e:l_e+1] = signmatrix @ klocal @ r_t @ i_d[k][:, f_e:l_e+1]
            
            
            #Include possible hinges on the first and the last element.
            if f_e_releases[0]==1 and f_e_releases[1]==1:
                k_mod = include_releases(klocal,1,1)
                if_loadgroup[:,f_e]=signmatrix @ k_mod @ r_t @ i_d[k][:,f_e]
           
            else:
                if f_e_releases[0]==1:
                    k_mod =include_releases(klocal,1,0)
                    if_loadgroup[:,f_e]=signmatrix @ k_mod @ r_t @ i_d[k][:,f_e]
                if l_e_releases[1]==1:
                    k_mod = include_releases(klocal,0,1)
                    if_loadgroup[:,l_e]=signmatrix @ k_mod @ r_t @ i_d[k][:,l_e]
            
        internal_forces_displacements.append(internal_forces_loadgroup)    
    
    return internal_forces_displacements