# -*- coding: utf-8 -*-
"""
Created on Fri May 24 14:05:46 2019

@author: umorf
"""
"""
This module contains the function to calculate the state of the points of
interest after having calculated the displacements and the internal forces 
at the discretization nodes.
"""

import numpy as np
from .assembly.shape_functions import *
from .assembly.rotation_matrix import get_rotation_matrix
import scipy.integrate as integrate


def calculate_state_poi(loads, points_of_interest, discretization_information,
                        internal_displacements_matrices, internal_forces_matrices):
    """Calculates the displacements and the internal forces of all points of interest.
    
    In a first step the data is calculated pointwise. Afterwards it is reordered
    elementwise.
    
    Arguments:
        loads                           -- a list containing the loadgroups of 
                                           the model
        points_of_interest              -- a list of points, for which the state
                                           is to be calculated
        discretization_information      -- the dictionary containing the 
                                           information of the discretized system
        internal_displacements_matrices -- the matrices storing the elementwise
                                           displacements (left and right) of 
                                           each loadgroup
        internal_forces_matrices        -- the matrices storing the elementwise
                                           internal forces (left and right) of 
                                           each loadgroup
        
    Return values:
        displacements_dictionaries   -- the dictionary containing the 
                                        displacements of the points of interest
        internal_forces_dictionaries -- the dictionary containing the internal 
                                        forces of the points of interest
    """
    
    beams_information   = discretization_information['Beams Information']
    elements_lists      = discretization_information['Elements']
    
    displacement_list    =[]
    internal_forces_list =[]
    
    #Calculate the data pointwise.
    for point_of_interest in points_of_interest[0]:
        
        #Get all necessary information
        beam_nr         = point_of_interest[0]
        poi_distance    = point_of_interest[1]
        element_length  = beams_information[beam_nr][3]
        theta           = beams_information[beam_nr][1]
        j_element       = max(int(np.ceil(poi_distance / element_length)-1),0)
        j_element       = min(beams_information[beam_nr][2]-1,j_element)
        element_distance= j_element*element_length
        dif_distance    = poi_distance - element_distance
        element_nr      = elements_lists[beam_nr][j_element]
        
        #Get the points displacements.
        poi_displacements = get_poi_displacement(element_nr, element_length,
                                                 theta, dif_distance,
                                                 internal_displacements_matrices)
        
        #Get the points intrenal forces.
        poi_internal_forces = get_poi_internal_forces(loads, beam_nr, theta,
                                                      element_nr, element_distance,
                                                      poi_distance,
                                                      internal_forces_matrices)
        
        displacement_list.append(poi_displacements)
        internal_forces_list.append(poi_internal_forces)
        
    #Reorder the lists loadgroupwise.
    displacements_dictionaries =[]
    internal_forces_dictionaries =[]
    
    #Build the lists for every loadgroup
    for i in range(len(loads)):
        dx_list  =[]
        dy_list  =[]
        drz_list =[]
        n_list   =[]
        v_list   =[]
        m_list   =[]
        
        #Build the lists which include all values of a loadcase.
        for j in range(len(points_of_interest[0])):
            dx_list.append(displacement_list[j][i][0])
            dy_list.append(displacement_list[j][i][1])
            drz_list.append(displacement_list[j][i][2])
            n_list.append(internal_forces_list[j][i][0])
            v_list.append(internal_forces_list[j][i][1])
            m_list.append(internal_forces_list[j][i][2])
        
        #Create the dictionaries.
        displacements_dictionary={'Displacement X':dx_list,
                                  'Displacement Y':dy_list,
                                  'Rotation Z':drz_list}
        
        internal_forces_dictionary={'Normal Force':n_list,
                                    'Shear Force':v_list,
                                    'Moment':m_list}
        
        displacements_dictionaries.append(displacements_dictionary)
        internal_forces_dictionaries.append(internal_forces_dictionary)
    
    return displacements_dictionaries, internal_forces_dictionaries

def get_poi_displacement(element_nr, element_length, theta, distance,
                         internal_displacements_matrices):
    """Calculates the displacements of the point of interest on the corresponding element.
    
    The calculation uses the shape functions and is therefore an approximation
    even for the case of infinite shear stiffness.
    
    Arguments:
        element_nr                      -- the number of the element on which 
                                           the point of interest is located
        element_length                  -- the length of the element on which 
                                           the point of interest is located
        theta                           -- the orientation of the local 
                                           coordinate systems (the inclination 
                                           of the beam)
        distance                        -- the distance of the point of interest
                                           from the starting node
        internal_displacements_matrices -- the matrices storing the elementwise
                                           internal forces (left and right) of 
                                           each loadgroup
        
    Return values:
        poi_displacements -- a list of the displacements of the point of 
                             interest for each loadgroup
    """
    
    poi_displacements = []
    r                 = get_rotation_matrix(theta)
    r_t               = r.transpose()
    i_d_matrices      = internal_displacements_matrices
    for i in range(len(internal_displacements_matrices)):
        local_nodal_displacements = r_t @ i_d_matrices[i][:,element_nr]

        x_left   = local_nodal_displacements[0]
        y_left   = local_nodal_displacements[1]
        rz_left  = local_nodal_displacements[2]
        
        x_right  = local_nodal_displacements[3]
        y_right  = local_nodal_displacements[4]
        rz_right = local_nodal_displacements[5]
        l = element_length

        dx=     x_left  * n1(distance, l)  + x_right  * n2(distance, l)
        dy=  (  y_left  * n3(distance, l)  + y_right  * n5(distance, l)
              + rz_left * n4(distance, l)  + rz_right * n6(distance, l))
        drz= (  y_left  * n31(distance, l) + y_right  * n51(distance, l)
              + rz_left * n41(distance, l) + rz_right * n61(distance, l))
        
        global_displacements = r[0:3,0:3] @ np.array([dx,dy,drz])
        
        poi_displacements.append([global_displacements[0],
                                  global_displacements[1],
                                  global_displacements[2]])
    
    return poi_displacements

def get_poi_internal_forces(loads, beam_nr, theta, element_nr, element_distance,
                            poi_distance, internal_forces_matrices):
    """Calculates the displacements of the point of interest on the corresponding element.
    
    Arguments:
        loads                    -- a list containing the loadgroups of the model
        beam_nr                  -- the number of the beam on which the point is
                                    located
        theta                    -- the orientation of the local coordinate 
                                    systems (the inclination of the beam)
        element_nr               -- the number of the element on which the point
                                    is located
        element_distance         -- the distance of the element to the beams 
                                    starting node
        poi_distance             -- the distance of the point of interest to the
                                    beams starting node
        internal_forces_matrices -- the matrices storing the elementwise internal
                                    forces (left and right) of each loadgroup
    
    Return values:
        poi_internal_forces -- a list of the internal forces of the point of
                               interest for each loadgroup
    """
    
    poi_internal_forces=[]
    for loadgroup_nr, loadgroup in enumerate(loads,0):
        
        #The value on the left side of the element.
        n_left   = internal_forces_matrices[loadgroup_nr][0,element_nr]
        v_left   = internal_forces_matrices[loadgroup_nr][1,element_nr]
        m_left   = internal_forces_matrices[loadgroup_nr][2,element_nr]
        
        #The influence of the shear force.
        forces_toadd=np.array([0, 0, v_left*(poi_distance-element_distance)])
        
        #The influence of the different loadtypes.
        
        if 'Point' in loadgroup and loadgroup['Point']:
            for point_load in loadgroup['Point']:
                if (point_load[0]==beam_nr and element_distance<point_load[1] 
                    and poi_distance>point_load[1]):
                    
                    distance = (poi_distance-point_load[1])
                    
                    forces_toadd[0] -= np.cos(theta)*point_load[2]
                    forces_toadd[0] -= np.sin(theta)*point_load[3]
                    forces_toadd[1] -= np.sin(theta)*point_load[2]
                    forces_toadd[1] += np.cos(theta)*point_load[3]
                    forces_toadd[2] -= point_load[4]
                    forces_toadd[2] -= np.sin(theta)*point_load[2]*distance
                    forces_toadd[2] += np.cos(theta)*point_load[3]*distance
         
        if 'Distributed' in loadgroup and loadgroup['Distributed']:
            for distributed_load in loadgroup['Distributed']:
                if (distributed_load[0]==beam_nr 
                    and element_distance<distributed_load[2]
                    and poi_distance>distributed_load[1]):
                    
                    #Defining the borders of the integration.
                    integration_start = max(element_distance, distributed_load[1])
                    integration_end   = min(poi_distance, distributed_load[2])
                    
                    #Calculate and update the forces for each direction.
                    for i in range(3):
                        fun=distributed_load_function(distributed_load, i)
                        forces_toadd+=calculate_forces_toadd(fun,theta,i,poi_distance,
                                                             integration_start,
                                                             integration_end)
        
        if 'Functions' in loadgroup and loadgroup['Functions']:
            for load_function in loadgroup['Functions']:
                if (load_function[0]==beam_nr 
                    and element_distance<load_function[2] 
                    and poi_distance>load_function[1]):
                    #Defining the borders of the integration.
                    integration_start = max(element_distance, load_function[1])
                    integration_end   = min(poi_distance, load_function[2])
                    
                    #Calculate and update the forces for each direction.
                    for i in range(3):
                        forces_toadd+=calculate_forces_toadd(load_function[3+i],
                                                             theta,i,poi_distance,
                                                             integration_start,
                                                             integration_end)
        
        #Include all of the loads influences on the internal forces of the
        # current loadgroup.
        poi_internal_forces.append([n_left+forces_toadd[0],
                                    v_left+forces_toadd[1],
                                    m_left+forces_toadd[2]])
    
    return poi_internal_forces
    
def distributed_load_function(distributed_load, direction):
    """Creates a load function out of the distributed load.
    
    Keyword argument:
        distributed_load -- a single distributed load
        direction -- the direction of interest of the distributed load
        
    Return values:
        function_load -- the load function of the specified direction
    """
    def function_load(x):
        q=(distributed_load[3+direction]+x/(distributed_load[2]-distributed_load[1])
          *(distributed_load[6+direction]-distributed_load[3+direction]))
        return q
    
    return function_load


def calculate_forces_toadd(function, theta, direction ,poi_distance,
                           integration_start, integration_end):
    """Calculates influence of a loadfunction on the internal forces at a point of interest 
    
    Keyword arguments:
        function          -- the load function in a specified direction
        theta             -- the orientation of the local coordinate systems 
                             (the inclination of the beam)
        direction         -- described in which global direction the force is 
                             acting.
        poi_distance      -- the distance of the point of interest to the beams
                             starting node
        integration_start -- the start of the integration (either the loads 
                             start or the start of the element)
        integration_end   -- the end of the integration (either the loads end 
                             or the distance of the point of interest)
    
    Return values:
        forces_toadd -- the internal forces deviating from the unloaded element
                        because of the calculated load function
    """
    
    forces_toadd=np.zeros((3))
    
    #Calculation according to the direction of the load.
    if direction==0 and function!=0 and function!=None:
        forces_toadd[0] = -np.cos(theta)*integrate.quad(function,integration_start,
                                                        integration_end)[0]
        forces_toadd[1] = -np.sin(theta)*integrate.quad(function,integration_start,
                                                        integration_end)[0]
        forces_toadd[2] = -np.sin(theta)*integrate.quad((lambda x: function(x)
                                                        *(poi_distance-x)),
                                                        integration_start,
                                                        integration_end)[0]
        
    if direction ==1 and function!=0 and function!=None:
        forces_toadd[0] = -np.sin(theta)*integrate.quad(function,integration_start,
                                                        integration_end)[0]
        forces_toadd[1] =  np.cos(theta)*integrate.quad(function,integration_start,
                                                        integration_end)[0]
        forces_toadd[2] =  np.cos(theta)*integrate.quad((lambda x: function(x)
                                                        *(poi_distance-x)),
                                                         integration_start,
                                                         integration_end)[0]
        
    if direction ==2 and function!=0 and function!=None:
        forces_toadd[2] = -integrate.quad(function,integration_start,integration_end)[0]
        
    return forces_toadd