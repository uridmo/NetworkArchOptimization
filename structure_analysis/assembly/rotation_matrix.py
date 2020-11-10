# -*- coding: utf-8 -*-
"""
Created on Tue May 14 06:45:44 2019

@author: umorf

The module contains the function which creates the rotation matrix.
"""

import numpy as np

def get_rotation_matrix(theta):
    """Gives the rotation matrix from a local to a global coordinate system.
    
    Arguments:
        theta -- the orientation of the local coordinate systems (the
                 inclination of the beam) 
    
    Return values:
        rotation_matrix -- the rotation matrix from local to global coordinates 
    """
    #The cases theta == +-pi/2 are treated separately, because the cosines of 
    # +-pi/2 are not equal to zero (machine precision). This would lead to the
    # creation of many almost zero elements in the sparse stiffness matrix.
    if theta==np.pi/2:
        r=np.array([[     0,     -1,      0,     0,    0,    0],
                    [     1,      0,      0,     0,    0,    0],
                    [     0,      0,      1,     0,    0,    0],
                    [     0,      0,      0,     0,   -1,    0],
                    [     0,      0,      0,     1,    0,    0],
                    [     0,      0,      0,     0,    0,    1]])
    
    elif theta==-np.pi/2:
        r=np.array([[     0,      1,      0,     0,    0,    0],
                    [    -1,      0,      0,     0,    0,    0],
                    [     0,      0,      1,     0,    0,    0],
                    [     0,      0,      0,     0,    1,    0],
                    [     0,      0,      0,    -1,    0,    0],
                    [     0,      0,      0,     0,    0,    1]])
    
    else:
        r=np.array([[np.cos(theta), -np.sin(theta),      0,              0,              0,      0],
                    [np.sin(theta),  np.cos(theta),      0,              0,              0,      0],
                    [            0,              0,      1,              0,              0,      0],
                    [            0,              0,      0,  np.cos(theta), -np.sin(theta),      0],
                    [            0,              0,      0,  np.sin(theta),  np.cos(theta),      0],
                    [            0,              0,      0,              0,              0,      1]])
    
    return r