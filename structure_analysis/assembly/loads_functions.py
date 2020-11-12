# -*- coding: utf-8 -*-
"""
Created on Tue May 14 07:05:08 2019

@author: umorf

The module contains the functions to assemble functional loads. It provides the
result in a special format which will be used to create the force matrix and to 
calculate the internal forces.
"""

import numpy as np
import scipy.integrate as integrate

from .shape_functions import *


def assemble_functional_loads(nodes_lists, elements_lists, beams_information,
                              function_loads):
    """Assembles global load functions into assembled nodal forces.
    
    Arguments:
        nodes_lists       -- a list containing for each beam an ordered list of
                             the node numbers along the beam
        elements_lists    -- a list containing for each beam a list of the 
                             elements on the beam in consecutive order
        beams_information -- a list containing for each beam its main information:
                             beam length, beam orientation, number of elements 
                             created on the beam, length of these elements 
        function_loads    -- a list containing the functional loads of a 
                             loadgroup
    
    Return values:
        assembled_forces -- a list containing for an assembled load its element
                            number, the two node numbers, the orientation and
                            its nodal forces
    """
    assembled_forces=[]
    
    #Append the assembled forces, iterating over all the loads.
    for function_load in function_loads:
                
        beam_nr         = function_load[0]
        x_start         = function_load[1]
        x_end           = function_load[2]
        theta           = beams_information[beam_nr][1]
        length_element  = beams_information[beam_nr][3]
        amount_elements = beams_information[beam_nr][2]

        
        #Calculate on which element the load's start and end is located.
        # j does not correspond to the elements number. But to the elements
        # number starting from zero on each beam.
        j_start = int(x_start // length_element)
        j_end   = int(np.ceil(x_end / length_element)-1)
        j_end   = min(amount_elements-1,j_end)
        
        #Calculate the distance from the segments start to the loads start and
        # end on the corresponding element.
        xl_start = x_start - (j_start * length_element)
        xr_end   = x_end - (j_end * length_element)
        xr_end   = min(length_element, xr_end)
        
        #Append the assembled forces list with an entry for each partially or
        # entirely loaded element.
        
        #Normal Case: The distributed load is stretched across multiple elements.    
        if j_end != j_start:
            # 1) Calculate the first (partially) loaded element
            
            local_nodal_forces = calculate_nodal_forces(function_load, theta,
                                                        length_element, j_start,
                                                        xl_start, length_element)
            append_assembled_forces(assembled_forces, nodes_lists, elements_lists,
                                    local_nodal_forces, beam_nr, j_start, theta)

            # 2) Calculate the last (partially) loaded element
            local_nodal_forces = calculate_nodal_forces(function_load, theta,
                                                        length_element, j_end,
                                                        0, xr_end)
            
            append_assembled_forces(assembled_forces, nodes_lists, elements_lists,
                                    local_nodal_forces, beam_nr, j_end, theta)

            # 3) Calculate the remaining elements (all entirely loaded)
            for j in range(j_start+1,j_end):
                local_nodal_forces = calculate_nodal_forces(function_load, theta,
                                                            length_element, j,
                                                            0, length_element)
                append_assembled_forces(assembled_forces, nodes_lists, elements_lists,
                                        local_nodal_forces, beam_nr, j, theta)


        #Special Case: Entire Load is within one element.
        else:
            # Calculate the only loaded element
            local_nodal_forces = calculate_nodal_forces(function_load, theta,
                                                        length_element, j_start,
                                                        xl_start, xr_end)
            append_assembled_forces(assembled_forces, nodes_lists, elements_lists,
                                    local_nodal_forces, beam_nr, j_start, theta)

    return assembled_forces

 
def multiply_functions(shape_function, function, length_element, x_start):
    """Gives the function of the product of a shape function and another function.
    
    The shape functions starts from zero, whereas the (load) function starts from
    the value x_start. 
    
    Arguments:
        shape_function -- a shape function
        function       -- a function which will be multiplied by the shape
                          function
        length         -- the length needed to determine the shape function
        x_start        -- the distance of the functions start on the element

    Returned values:
        multiplied_function -- a function giving the product of the shape
                               function and the load function
    """
    def multiplied_function(x):
        return shape_function(x,length_element)*function(x+x_start)
    
    return multiplied_function

 
def calculate_nodal_forces(function_load, theta, length_element, j, x_left, x_right):
    """"Calculates the nodal forces on an element resulting from a load function.
    
    Arguments:
        function_load    -- a single functional load a dictionary containing the
                            loadgroups loads in different loadtypes  
        theta            -- the orientation of the local coordinate systems 
                            (the inclination of the beam)
        length_element   -- the length of the element
        j                -- the number of the left node along the beam starting
                            from zero
        x_left           -- the distance of the loads start on the element to
                            the left node
        x_right          -- the distance of the loads end on the element to the
                            left node
        
    Return values:
        local_nodal_forces -- a numpy vector of the assembled local nodal forces 
                              on the left and the right side of the element
    
    """
    fun = function_load
    l   = length_element
    l0  = j * length_element
    xl  = x_left
    xr  = x_right
    
    forces = np.zeros((6,1))
    
    #Calculate the nodal forces for each function component which is not zero
    if fun[3]!=0 and fun[3]!=None:
        forces[0] +=  np.cos(theta) * integrate.quad(multiply_functions(n1,fun[3],l,l0),xl,xr)[0]
        forces[1] += -np.sin(theta) * integrate.quad(multiply_functions(n3,fun[3],l,l0),xl,xr)[0]
        forces[2] += -np.sin(theta) * integrate.quad(multiply_functions(n4,fun[3],l,l0),xl,xr)[0]
        forces[3] +=  np.cos(theta) * integrate.quad(multiply_functions(n2,fun[3],l,l0),xl,xr)[0]
        forces[4] += -np.sin(theta) * integrate.quad(multiply_functions(n5,fun[3],l,l0),xl,xr)[0]
        forces[5] += -np.sin(theta) * integrate.quad(multiply_functions(n6,fun[3],l,l0),xl,xr)[0]
        
    if fun[4]!=0 and fun[4]!=None:
        forces[0] += np.sin(theta) * integrate.quad(multiply_functions(n1,fun[4],l,l0),xl,xr)[0]
        forces[1] += np.cos(theta) * integrate.quad(multiply_functions(n3,fun[4],l,l0),xl,xr)[0]
        forces[2] += np.cos(theta) * integrate.quad(multiply_functions(n4,fun[4],l,l0),xl,xr)[0]
        forces[3] += np.sin(theta) * integrate.quad(multiply_functions(n2,fun[4],l,l0),xl,xr)[0]
        forces[4] += np.cos(theta) * integrate.quad(multiply_functions(n5,fun[4],l,l0),xl,xr)[0]
        forces[5] += np.cos(theta) * integrate.quad(multiply_functions(n6,fun[4],l,l0),xl,xr)[0]
        
    if fun[5]!=0 and fun[5]!=None:
        forces[1] += integrate.quad(multiply_functions(n31,fun[5],l,l0),xl,xr)[0]
        forces[4] += integrate.quad(multiply_functions(n51,fun[5],l,l0),xl,xr)[0]
        forces[2] += integrate.quad(multiply_functions(n41,fun[5],l,l0),xl,xr)[0]
        forces[5] += integrate.quad(multiply_functions(n61,fun[5],l,l0),xl,xr)[0]
    
    local_nodal_forces = forces

    return local_nodal_forces

 
def append_assembled_forces(assembled_forces, nodes_lists, elements_lists,
                            local_nodal_forces, beam_nr, j, theta):
    """Appends the assembled_forces list with the information of an assembled load.
    
    Arguments:
        assembled_forces   -- a list containing for each loaded element the 
                              assembled nodal forces, the two node numbers and 
                              the orientation 
        nodes_lists        -- a list containing for each beam an ordered list of
                              the node numbers along the beam 
        elements_lists     -- a list containing for each beam a list of the 
                              elements on the beam in consecutive order 
        local_nodal_forces -- the assembled local nodal forces
        beam_nr            -- the number of the loaded beam
        j                  -- the number of the left node along the beam 
                              starting from zero
        theta              -- the orientation of the local coordinate systems 
                              (the inclination of the beam)         
    """
    
    segment_nr = elements_lists[beam_nr][j]
    node_left  = nodes_lists[beam_nr][j]
    node_right = nodes_lists[beam_nr][j+1]
            
    assembled_force = [segment_nr, node_left, node_right, theta, local_nodal_forces]
    
    assembled_forces.append(assembled_force)
    
    return