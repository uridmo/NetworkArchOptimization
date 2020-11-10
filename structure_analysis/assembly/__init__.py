# -*- coding: utf-8 -*-
"""
Created on Mon May 13 20:21:44 2019

@author: umorf

The module initializes the subpackage and contains the assemble function. It 
builds the stiffness matrix and the force matrix of the system.
"""

from .stiffness_matrix import get_stiffness_matrix
from .force_matrix import get_force_matrices
from .initial_displacements import apply_initial_displacements

def assemble(model,discretization_information):
    """Assembles the stiffness matrix of the system and the force matrix of the loadgroups.
    
    The initial displacements are handled separately from the other load types,
    because it uses the stiffness matrix. It might be subject to change in order
    to include initial displacements on unrestricted nodes.
    
    Arguments:
        model                      -- the structural model as a dictionary: 
                                      Containing the nodes, beams, loads and 
                                      boundary conditions
        discretization_information -- the dictionary containing the information
                                      of the discretized system
    
    Return values:
        stiffness_matrix         -- the stiffness matrix of the system, not 
                                    including restricted degrees
        force_matrix             -- a matrix combining the global force vectors 
                                    of the different loadgroups
        internal_forces_assembly -- a list of matrices saving the internal 
                                    forces for each loadgroup resulting from 
                                    assembling its loads
    """
    
    #Get the required information from the input.
    nodes_lists         = discretization_information['Nodes']
    elements_lists      = discretization_information['Elements']
    releases_beams      = discretization_information['Releases']['Beams']
    releases_elements   = discretization_information['Releases']['Elements']
    beams_information   = discretization_information['Beams Information']
    
    beams_stiffness     = model['Beams']['Stiffness']
    loads               = model['Loads']
    
    #Assemble Stiffness Matrix
    stiffness_matrix = get_stiffness_matrix(beams_stiffness, nodes_lists,
                                            releases_beams, beams_information)
    
    #Assemble Global Force Matrix and Internal Force Matrices
    force_matrix, internal_forces_assembly = get_force_matrices(loads, 
                                                                nodes_lists,
                                                                elements_lists,
                                                                releases_elements,
                                                                beams_information)
    
    #Applies the initial displacements on the restricted degrees
    apply_initial_displacements(loads, stiffness_matrix, force_matrix)
    
    return stiffness_matrix, force_matrix, internal_forces_assembly