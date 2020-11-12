# -*- coding: utf-8 -*-
"""
Created on Tue May 14 06:46:24 2019

@author: umorf

The module contains the functions to create a local stiffness matrix and to
modify it to take into account releases.
"""

from copy import deepcopy

import numpy as np


def get_local_stiffness_matrix(length, beam_stiffness):
    """Returns the local stiffness matrix of a beam element.
    
    It handles the cases of infinite and finite shear stiffnesses. Infinite 
    shear stiffness is assumed if the third element of beam_stiffness is either
    zero or None or omited.
    
    It does not include releases. (This is done in a separate function named
    include_releases)
    
    Arguments:
        length         -- the length of the beams elements 
        beam_stiffness -- a beams normal, beding (and shear) stiffnesses 
    
    Return values:
        local_stiffness_matrix -- the local stiffness matrix of a beam element 
                                  the stiffness matrix of the system, not 
                                  including restricted degrees
    """
    #Get the length an the normal and bending stiffness of the beam element.
    l=length
    ea=float(beam_stiffness[0])
    ei=float(beam_stiffness[1])
    
    #Infinite shear stiffness.
    if len(beam_stiffness)==2 or beam_stiffness[2]==None or beam_stiffness[2]==0:
            
        local_stiffness_matrix=np.array([[ ea/l,              0,            0,   -ea/l,            0,           0],
                                         [    0,     12*ei/l**3,    6*ei/l**2,       0,  -12*ei/l**3,   6*ei/l**2],
                                         [    0,      6*ei/l**2,    4*ei/l**1,       0,   -6*ei/l**2,   2*ei/l**1],
                                         [-ea/l,              0,            0,    ea/l,            0,           0],
                                         [    0,    -12*ei/l**3,   -6*ei/l**2,       0,   12*ei/l**3,  -6*ei/l**2],
                                         [    0,      6*ei/l**2,    2*ei/l**1,       0,   -6*ei/l**2,   4*ei/l**1]],
                                         dtype='float64')
    #Finite shear stiffness.
    else:
        #Get the shear stiffness and the helper variable phi.
        ga=float(beam_stiffness[2])
        phi=12*ei/(ga*l**2)
                
        local_stiffness_matrix=np.array([[ ea/l,                        0,                         0,    -ea/l,                      0,                        0],
                                         [    0,     12*ei/(l**3*(1+phi)),       6*ei/(l**2*(1+phi)),        0,  -12*ei/(l**3*(1+phi)),      6*ei/(l**2*(1+phi))],
                                         [    0,      6*ei/(l**2*(1+phi)),    (4+phi)*ei/(l*(1+phi)),        0,   -6*ei/(l**2*(1+phi)),   (2-phi)*ei/(l*(1+phi))],
                                         [-ea/l,                        0,                         0,     ea/l,                      0,                        0],
                                         [    0,    -12*ei/(l**3*(1+phi)),      -6*ei/(l**2*(1+phi)),        0,   12*ei/(l**3*(1+phi)),     -6*ei/(l**2*(1+phi))],
                                         [    0,      6*ei/(l**2*(1+phi)),    (2-phi)*ei/(l*(1+phi)),        0,   -6*ei/(l**2*(1+phi)),   (4+phi)*ei/(l*(1+phi))]],
                                         dtype='float64')
        
    return local_stiffness_matrix

def include_releases(local_stiffness_matrix, release_start, release_end):
    """Modifies the stiffness matrix to include releases on either sides.
    
    Arguments:
        local_stiffness_matrix -- the stiffness matrix of the system, not including 
                                  restricted degrees
        release_start          -- the type of the release at the start of the 
                                  element
        release_end            -- the type of the release at the end of the 
                                  element
        
    Return values:
        stiffness_matrix_modified -- the stiffness matrix of the beam element 
                                     including hinges on at its start or end
    """
    #Get a copy of the stiffness matrix that can be modified.
    stiffness_matrix_modified = deepcopy(local_stiffness_matrix)
    
    #Modify the stiffness matrix in case the releases are hinged.
    if release_start==1:
        stiffness_matrix_modified -= (stiffness_matrix_modified[:,2].reshape((6,1))
                                     @ (stiffness_matrix_modified[2,:].reshape((1,6))
                                        / stiffness_matrix_modified[2,2]))
    if release_end==1:
        stiffness_matrix_modified -= (stiffness_matrix_modified[:,5].reshape((6,1))
                                      @ (stiffness_matrix_modified[5,:].reshape((1,6))
                                         / stiffness_matrix_modified[5,5]))

    return stiffness_matrix_modified