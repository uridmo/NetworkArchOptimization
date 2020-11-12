# -*- coding: utf-8 -*-
"""
Created on Tue May 14 07:05:08 2019

@author: umorf

The module contains the functions to assemble distributed loads. It provides 
the result in a special format which will be used to create the force matrix 
and to calculate the internal forces.
"""

import numpy as np

from .rotation_matrix import get_rotation_matrix


def assemble_distributed_loads(nodes_lists, elements_lists, beams_information,
                               distributed_loads):
    """Assembles distributed loads into assembled nodal forces.
    
    In a first step it calculates the first and the last loaded segment. For
    these ones a complex expression for partially loaded beams is used. For the
    other elements which are entirely loaded, a simplified expression is used.
    
    The nodal forces are returned in a list together with other information
    needed to assembly to global force matrix and the internal forces.
    
    Arguments:
        nodes_lists       -- a list containing for each beam an ordered list of
                             the node numbers along the beam
        elements_lists    -- a list containing for each beam a list of the 
                             elements on the beam in consecutive order
        beams_information -- a list containing for each beam its main information:
                             beam length, beam orientation, number of elements 
                             created on the beam, length of these elements 
        distributed_loads -- a list containing the distributed loads of a 
                             loadgroup
    
    Return values:
        assembled_forces -- a list containing for an assembled load its element
                            number, the two node numbers, the orientation and
                            its nodal forces
    """
    assembled_forces=[]
    
    #Append the assembled forces, iterating over all the loads
    for distributed_load in distributed_loads:
        
        beam_nr         = distributed_load[0]
        x_start         = distributed_load[1]
        x_end           = distributed_load[2]
        length_load     = x_end-x_start
        length_element  = beams_information[beam_nr][3]
        amount_elements = beams_information[beam_nr][2]

        
        #Rotate into local coordinates
        theta   = beams_information[beam_nr][1]
        r       = get_rotation_matrix(theta)
        load_local = r.transpose() @ distributed_load[3:9]
        
        #Calculate the value at the start of the beam and the inclination per element
        load_inclination = ((load_local[3:6]-load_local[0:3])/length_load*length_element)
        
        load_start = load_local[0:3]-(load_inclination/length_element*x_start)
        
        #Calculate on which element the load's start and end is located.
        # j does not correspond to the elements number. But to the elements
        # number starting from zero on each beam.
        j_start = int(x_start // length_element)
        j_end   = int(np.ceil(x_end / length_element)-1)
        j_end   = min(amount_elements-1,j_end)
        
        #Calculate the position of the loads start and end on the according element
        xl_start = x_start - (j_start * length_element)
        xr_end   = x_end - (j_end * length_element)
        xr_end   = min(length_element, xr_end)
        
        #Append the assembled forces list with an entry for each partially or
        # entirely loaded element.
        #Normal Case: The distributed load is stretched across multiple elements.    
        if j_end != j_start:
            # 1) Calculate the first (partially) loaded element
            local_nodal_forces = calculate_nodal_forces(load_start,
                                                        load_inclination,
                                                        j_start, length_element,
                                                        xl_start, length_element)
            append_assembled_forces(assembled_forces, nodes_lists, elements_lists,
                                    local_nodal_forces, beam_nr, j_start, theta)

            # 2) Calculate the last (partially) loaded element
            local_nodal_forces = calculate_nodal_forces(load_start, 
                                                        load_inclination,
                                                        j_end, length_element,
                                                        0, xr_end)
            append_assembled_forces(assembled_forces, nodes_lists, elements_lists,
                                    local_nodal_forces, beam_nr, j_end, theta)

            # 3) Calculate the remaining elements (all entirely loaded)
            for j in range(j_start+1,j_end):
                local_nodal_forces = calculate_nodal_forces(load_start,
                                                            load_inclination,
                                                            j, length_element,
                                                            0, length_element)
                append_assembled_forces(assembled_forces, nodes_lists, elements_lists,
                                        local_nodal_forces, beam_nr, j, theta)



        #Special Case: Entire Load is within one element.
        else:
            # Calculate the only loaded element
            local_nodal_forces = calculate_nodal_forces(load_start, 
                                                        load_inclination,
                                                        j_start, length_element,
                                                        xl_start, xr_end)
            append_assembled_forces(assembled_forces, nodes_lists, elements_lists,
                                    local_nodal_forces, beam_nr, j_end, theta)
            
    return assembled_forces

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

 
def calculate_nodal_forces(load_start, load_inclination, j, length_element,
                           x_left, x_right):
    """Calculates the nodal forces on an element resulting from a distributed load.
    
    It distinguishes between entirely loaded elements and partially loaded
    segments.
    
    Arguments:
        load_start       -- a numpy vector of the value of the distributed load
                            at the beginning of the hypothetically entirely loaded beam.
        load_inclination -- a numpy vector of the inclination of the load
                            between two nodes
        j                -- the number of the left node along the beam starting
                            from zero
        length_element   -- the length of the element
        x_left           -- the distance of the loads start on the element to
                            the left node
        x_right          -- the distance of the loads end on the element to the
                            left node
        
        (On a entirely loaded element x_left corresponds to 0 and x_right
        corresponds to the elements length)
        
    Return values:
        local_nodal_forces -- a numpy vector of the assembled local nodal forces 
                              on the left and the right side of the element
    """
    #Calculate the load at the left and the right node
    load_left   = load_start + load_inclination * j
    load_right  = load_start + load_inclination * (j+1)
    
    #Create short helper variables.
    l   = length_element
    xl  = x_left
    xr  = x_right
    
    qxl = load_left[0]
    qxr = load_right[0]
    qyl = load_left[1]
    qyr = load_right[1]
    mzl = load_left[2]
    mzr = load_right[2]
        
    #The easier case of an entirely loaded element.
    if xr==l and xl==0:
        Fx1 = (l*qxl)/3+(l*qxr)/6
        Fy1 = -(mzl/2)-mzr/2+(7*l*qyl)/20+(3*l*qyr)/20
        Mz1 = (l*mzl)/12-(l*mzr)/12+(l**2*qyl)/20+(l**2*qyr)/30
        Fx2 = (l*qxl)/6+(l*qxr)/3
        Fy2 = mzl/2+mzr/2+(3*l*qyl)/20+(7*l*qyr)/20
        Mz2 = -((l*mzl)/12)+(l*mzr)/12-(l**2*qyl)/30-(l**2*qyr)/20
    
    #The case of a partially loaded element.
    else:
        Fx1 = (-qxl*xl+(qxl*xl**2)/l-(qxr*xl**2)/(2*l)-(qxl*xl**3)/(3*l**2)
               +(qxr*xl**3)/(3*l**2)+qxl*xr-(qxl*xr**2)/l+(qxr*xr**2)/(2*l)
               +(qxl*xr**3)/(3*l**2)-(qxr*xr**3)/(3*l**2))
        
        Fy1 = (-qyl*xl+(3*mzl*xl**2)/l**2+(qyl*xl**2)/(2*l)-(qyr*xl**2)/(2*l)
               -(4*mzl*xl**3)/l**3+(2*mzr*xl**3)/l**3+(qyl*xl**3)/l**2
               +(3*mzl*xl**4)/(2*l**4)-(3*mzr*xl**4)/(2*l**4)-(5*qyl*xl**4)/(4*l**3)
               +(3*qyr*xl**4)/(4*l**3)+(2*qyl*xl**5)/(5*l**4)-(2*qyr*xl**5)/(5*l**4)
               +qyl*xr-(3*mzl*xr**2)/l**2-(qyl*xr**2)/(2*l)+(qyr*xr**2)/(2*l)
               +(4*mzl*xr**3)/l**3-(2*mzr*xr**3)/l**3-(qyl*xr**3)/l**2
               -(3*mzl*xr**4)/(2*l**4)+(3*mzr*xr**4)/(2*l**4)+(5*qyl*xr**4)/(4*l**3)
               -(3*qyr*xr**4)/(4*l**3)-(2*qyl*xr**5)/(5*l**4)+(2*qyr*xr**5)/(5*l**4))
        
        Mz1 = (-mzl*xl+(5*mzl*xl**2)/(2*l)-(mzr*xl**2)/(2*l)-(qyl*xl**2)/2
               -(7*mzl*xl**3)/(3*l**2)+(4*mzr*xl**3)/(3*l**2)+(qyl*xl**3)/l
               -(qyr*xl**3)/(3*l)+(3*mzl*xl**4)/(4*l**3)-(3*mzr*xl**4)/(4*l**3)
               -(3*qyl*xl**4)/(4*l**2)+(qyr*xl**4)/(2*l**2)+(qyl*xl**5)/(5*l**3)
               -(qyr*xl**5)/(5*l**3)+mzl*xr-(5*mzl*xr**2)/(2*l)+(mzr*xr**2)/(2*l)
               +(qyl*xr**2)/2+(7*mzl*xr**3)/(3*l**2)-(4*mzr*xr**3)/(3*l**2)
               -(qyl*xr**3)/l+(qyr*xr**3)/(3*l)-(3*mzl*xr**4)/(4*l**3)
               +(3*mzr*xr**4)/(4*l**3)+(3*qyl*xr**4)/(4*l**2)-(qyr*xr**4)/(2*l**2)
               -(qyl*xr**5)/(5*l**3)+(qyr*xr**5)/(5*l**3))
        
        Fx2 = (-((qxl*xl**2)/(2*l))+(qxl*xl**3)/(3*l**2)-(qxr*xl**3)/(3*l**2)
               +(qxl*xr**2)/(2*l)-(qxl*xr**3)/(3*l**2)+(qxr*xr**3)/(3*l**2))
        
        Fy2 = (-((3*mzl*xl**2)/l**2)+(4*mzl*xl**3)/l**3-(2*mzr*xl**3)/l**3
               -(qyl*xl**3)/l**2-(3*mzl*xl**4)/(2*l**4)+(3*mzr*xl**4)/(2*l**4)
               +(5*qyl*xl**4)/(4*l**3)-(3*qyr*xl**4)/(4*l**3)-(2*qyl*xl**5)/(5*l**4)
               +(2*qyr*xl**5)/(5*l**4)+(3*mzl*xr**2)/l**2-(4*mzl*xr**3)/l**3
               +(2*mzr*xr**3)/l**3+(qyl*xr**3)/l**2+(3*mzl*xr**4)/(2*l**4)
               -(3*mzr*xr**4)/(2*l**4)-(5*qyl*xr**4)/(4*l**3)+(3*qyr*xr**4)/(4*l**3)
               +(2*qyl*xr**5)/(5*l**4)-(2*qyr*xr**5)/(5*l**4))
        
        Mz2 = ((mzl*xl**2)/l-(5*mzl*xl**3)/(3*l**2)+(2*mzr*xl**3)/(3*l**2)
               +(qyl*xl**3)/(3*l)+(3*mzl*xl**4)/(4*l**3)-(3*mzr*xl**4)/(4*l**3)
               -(qyl*xl**4)/(2*l**2)+(qyr*xl**4)/(4*l**2)+(qyl*xl**5)/(5*l**3)
               -(qyr*xl**5)/(5*l**3)-(mzl*xr**2)/l+(5*mzl*xr**3)/(3*l**2)
               -(2*mzr*xr**3)/(3*l**2)-(qyl*xr**3)/(3*l)-(3*mzl*xr**4)/(4*l**3)
               +(3*mzr*xr**4)/(4*l**3)+(qyl*xr**4)/(2*l**2)-(qyr*xr**4)/(4*l**2)
               -(qyl*xr**5)/(5*l**3)+(qyr*xr**5)/(5*l**3))
    
    #Defines the local nodal forces into a vector.
    local_nodal_forces = np.array([[Fx1], [Fy1], [Mz1], [Fx2], [Fy2], [Mz2]])
    
    return local_nodal_forces