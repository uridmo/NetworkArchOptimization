# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 16:03:31 2019

@author: umorf

This module contains all the functions needed for solving of the system 
including its main function solve.
"""

import numpy as np
import scipy.sparse.linalg as spsl
from copy import deepcopy


def solve(stiffness_and_force_matrices, loads, boundary_conditions):
    """Solves the system and creates the displacement matrix and the support reactions list.
    
    It solves the modified system in a first step. Then it calculates the 
    support reactions with the supports stiffness matrix. Afterwards it inserts
    the restricted degrees and their initial displacements into the displacement
    matrix.
    
    In a last step the list of the support reactions is created from the support
    reactions matrix.
    
    Exceptions:
        If the displacement matrix contains any nan values.
        
    Arguments:
        stiffness_and_force_matrices -- the stiffness and force matrices of the
                                        restricted and the unrestricted nodal
                                        directions
        loads                        -- a list containing the loadgroups of the
                                        model
        boundary_conditions          -- the boundary conditions of the system
        
    Return values:
        displacements     -- a list of dictionaries containing for each loadgroup
                             the displacements of all beams nodes
        support_reactions -- a list of the restricted nodes and their support 
                             reactions
    """
    restricted_degrees = boundary_conditions['Restricted Degrees']
    stiffness_matrix_modified = stiffness_and_force_matrices[0]
    stiffness_matrix_supports = stiffness_and_force_matrices[1]
    force_matrix_modified = stiffness_and_force_matrices[2]
    force_matrix_supports = stiffness_and_force_matrices[3]

    # Solve the system.
    # spsolve provides fast results but the accuracy can become a problem in large models
    displacements_modified = spsl.spsolve(stiffness_matrix_modified, force_matrix_modified)

    # Raise an Exception if any of the values of the displacement matrix are nan.
    if (displacements_modified == np.nan).any():
        raise Exception('The displacement matrix contains NaN Elements. The'
                        'stiffness matrix is probably not regular.')

    # In case there was only one loadgroup the vector has to be converted to a matrix.
    if displacements_modified.ndim == 1:
        rows = displacements_modified.shape[0]
        displacements_modified = displacements_modified.reshape((rows, 1))

    # Calculate the support reactions including the assembled and omited support forces.
    support_reactions_matrix = stiffness_matrix_supports @ displacements_modified
    support_reactions_matrix -= force_matrix_supports

    # Include the restricted degrees and the initial displacements.
    displacements = insert_initial_displacements(displacements_modified, loads,
                                                 restricted_degrees)

    # Create the support reactions list.
    support_reactions = get_support_reactions(support_reactions_matrix,
                                              restricted_degrees)

    return displacements, support_reactions


def insert_initial_displacements(displacements_modified, loads, restricted_degrees):
    """Inserts the restricted degrees and initial displacements into the modified displacements.
    
    Arguments:
        displacements_modified -- the displacement matrix excluding the 
                                  restricted degrees
        loads                  -- a list containing the loadgroups of the model
        restricted_degrees     -- the restricted degrees of the system
        
    Return values:
        displacements -- a list of dictionaries containing for each loadgroup 
                         the displacements of all beams nodes
    """

    # Determine the sorted restricted nodes.
    restricted_nodes = []
    for restricted_degree in restricted_degrees:
        for i in range(3):
            if restricted_degree[i + 1] == 1:
                restricted_nodes.append(restricted_degree[0] * 3 + i)
    restricted_nodes.sort()

    # Determine where rows are to be inserted .
    rowstoinsert = deepcopy(restricted_nodes)
    for i in range(len(restricted_nodes)):
        rowstoinsert[i] -= i

    # Insert zero on these rows.
    displacements = np.insert(displacements_modified, rowstoinsert, 0, axis=0)

    # Add the initial displacements.
    for loadgroup_nr, loadgroup in enumerate(loads, 0):

        if 'Initial Displacements' in loadgroup and loadgroup['Initial Displacements']:

            for initial_displacement in loadgroup['Initial Displacements']:

                for i in range(3):
                    row = initial_displacement[0] * 3 + i
                    col = loadgroup_nr
                    displacements[row, col] += initial_displacement[i + 1]

    return displacements


def get_support_reactions(support_reactions_matrix, restricted_degrees):
    """Creates a list of the support reactions from the support reactions matrix.
    
    Arguments:
        support_reactions_matrix -- a matrix of the restricted nodes and their 
                                    support reactions
        restricted_degrees       -- the restricted degrees of the system
    
    Return values:
        support_reactions -- a list of the restricted nodes and their support 
                             reactions
    """
    amount_of_loadgroups = support_reactions_matrix.shape[1]

    # Append the list for each loadgroup
    support_reactions = []
    for k in range(amount_of_loadgroups):

        # The format is the same as in the restricted degrees.
        support_reactions_temp = deepcopy(restricted_degrees)

        # Get the support reactions for each restricted degree.
        counter = 0
        for rd_nr, restricted_degree in enumerate(restricted_degrees, 0):

            for i in range(3):
                if restricted_degree[i + 1] == 1:
                    support_reaction = round(support_reactions_matrix[counter, k], 5)
                    support_reactions_temp[rd_nr][i + 1] = support_reaction
                    counter += 1

        support_reactions.append(support_reactions_temp)

    return support_reactions
