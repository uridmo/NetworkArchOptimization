# -*- coding: utf-8 -*-
"""
Created on Mon May 13 21:24:07 2019

@author: umorf

The module contains the functions to build the global force matrix and the 
internal force matrix (from assembling). The functions to calculate the nodal
forces depending on the different loadtypes are used from separate modules. 
"""

import numpy as np
from scipy.sparse import csr_matrix
from copy         import deepcopy

from .rotation_matrix   import get_rotation_matrix
from .loads_point       import assemble_point_loads
from .loads_distributed import assemble_distributed_loads
from .loads_functions   import assemble_functional_loads

def get_force_matrices(loads, nodes_lists, elements_lists, releases_elements,
                       beams_information):
    """Assembles the global force matrix and the internal forces from the loads.
    
    It uses the separately defined loadtype assembling functions. These return
    the local element forces together with the element number, its orientation
    and its starting and ending node. (saved in assembled_forces)
    
    The assembled_forces variable is afterwards used to update the global force
    vector and the internal forces matrix of each loadgroup.
    
    The only exception are the 'Nodal' loads which are handled separately, since
    they cause no internal forces during assembling.
    
    Arguments:
        loads             -- a list containing the loadgroups of the model
        nodes_lists       -- a list containing for each beam an ordered list of
                             the node numbers along the beam
        elements_lists    -- a list containing for each beam a list of the 
                             elements on the beam in consecutive order
        releases_elements -- a dictionary saving the special releases to the 
                             corresponding element number
        beams_information -- a list containing for each beam its main information:
                             beam length, beam orientation, number of elements 
                             created on the beam, length of these elements
    
    Return values:
        force_matrix             -- a matrix combining the global force vectors
                                    of the different loadgroups
        internal_forces_assembly -- a list of matrices saving the internal forces
                                    for each loadgroup resulting from assembling 
                                    its loads
    """
    number_of_nodes = max([max(sublist)] for sublist in nodes_lists)[0] + 1
    
    number_of_elements   = elements_lists[-1][-1]+1
    number_of_loadgroups = len(loads)

    #Create the empty global force matrix.
    force_matrix = np.zeros((3*number_of_nodes, number_of_loadgroups))
    
    #Create the empty internal forces list.
    internal_forces_assembly=[]
    
    #Update the global force matrix and the internal forces list for each loadgroup.
    for loadgroup_nr, loadgroup in enumerate(loads,0):
        
        internal_forces_sparse_lists = [[],[],[]]
        
        #Get the force vector for the current loadgroup.
        force_vector = force_matrix[:,loadgroup_nr]
        
        
        #Update the global force vector for each loadtype and its internal forces
        if 'Nodal' in loadgroup and loadgroup['Nodal']:
            add_nodal_forces(force_vector,loadgroup['Nodal'])
            
        if 'Point' in loadgroup and loadgroup['Point']:
            assembled_forces=assemble_point_loads(nodes_lists, 
                                                  elements_lists,
                                                  beams_information,
                                                  loadgroup['Point'])
            add_assembled_forces(internal_forces_sparse_lists, force_vector,
                                 assembled_forces, releases_elements, 
                                 beams_information)
         
        if 'Distributed' in loadgroup and loadgroup['Distributed']:
            assembled_forces=assemble_distributed_loads(nodes_lists, 
                                                        elements_lists,
                                                        beams_information,
                                                        loadgroup['Distributed'])
            add_assembled_forces(internal_forces_sparse_lists, force_vector,
                                 assembled_forces, releases_elements, 
                                 beams_information)
            
        if 'Functions' in loadgroup and loadgroup['Functions']:
            assembled_forces=assemble_functional_loads(nodes_lists, 
                                                       elements_lists,
                                                      beams_information,
                                                      loadgroup['Functions'])
            add_assembled_forces(internal_forces_sparse_lists, force_vector,
                                 assembled_forces, releases_elements, 
                                 beams_information)
            
        #Create the internal forces matrix
        rows = internal_forces_sparse_lists[0]
        cols = internal_forces_sparse_lists[1]
        data = internal_forces_sparse_lists[2]
        
        internal_forces_toadd=csr_matrix((data, (rows, cols)),
                                          shape=(6, number_of_elements))
        
        #Add it to the list containing the internal force matrix of each loadgroup.
        internal_forces_assembly.append(internal_forces_toadd)
        
    return force_matrix, internal_forces_assembly
 
def add_nodal_forces(force_vector, loads_nodal):
    """Updates the global force vector with the nodal loads.
    
    Arguments:
        force_vector -- a single global force vector corresponding to one loadgroup
        loads_nodal -- the loads applied on nodes
    """
    for nodal_load in loads_nodal:
        nodeposition=nodal_load[0]*3
        force_vector[nodeposition:nodeposition+3]+=nodal_load[1:4]
    return
 
def add_assembled_forces(internal_forces_sparse_lists, force_vector,
                         assembled_forces, releases_elements, beams_information):
    """Adds assembled forces to the global force vector and the internal forces matrix.
    
    The function handles the modification of the assembled local forces into
    internal forces and global nodal forces. It also takes into account 
    possible hinges.
    
    Arguments:
        internal_forces_sparse_lists -- the temporary lists used to create the 
                                        sparse internal force matrix
        force_vector                 -- a single global force vector corresponding
                                        to one loadgroup
        assembled_forces             -- a list containing for each loaded element
                                        the assembled nodal forces, the two node
                                        numbers and the orientation
        releases_elements            -- a dictionary saving the special releases
                                        to the corresponding element number
        beams_information            -- a list containing for each beam its main
                                        information: beam length, beam orientation,
                                        number of elements created on the beam,
                                        length of these elements
    """
    signmatrix = np.diag(np.array([-1,1,-1,1,-1,1]))
    
    #Handle each entry of assembled forces.
    for assembled_element_forces in assembled_forces:

        element_nr  = assembled_element_forces[0]
        theta       = assembled_element_forces[3]
        startnode   = assembled_element_forces[1]
        endnode     = assembled_element_forces[2]
        
        assembled_force_vector = assembled_element_forces[4]
        
        nodespositions = [startnode*3, startnode*3+1, startnode*3+2,
                          endnode*3,   endnode*3+1,   endnode*3+2  ]
        
        #Special treatment for elements with hinged releases.
        #Normal elements:
        if element_nr not in releases_elements.keys():
            local_force_vector = assembled_force_vector
        #Hinged elements:    
        else:
            left_release  = releases_elements.get(element_nr,[0,0])[0]
            right_release = releases_elements.get(element_nr,[0,0])[1]
            
            element_length = get_element_length(element_nr, beams_information)
            
            local_force_vector = include_hinges(assembled_force_vector,
                                                element_length, left_release,
                                                right_release)
        
        #Rotate the local forces into global forces
        global_nodal_forces = get_rotation_matrix(theta) @ local_force_vector
        
        #Update the global force vector.
        force_vector[nodespositions] += global_nodal_forces[:,0]
        
        #Adapt the local forces to the orientation of the internal forces.
        local_internal_forces = signmatrix @ local_force_vector
        
        #Update the internal forces sparse lists.
        for j in range(6):
            if local_internal_forces[j][0]!=0:
                internal_forces_sparse_lists[2].append(local_internal_forces[j][0])
                internal_forces_sparse_lists[1].append(element_nr)
                internal_forces_sparse_lists[0].append(j)

    return
 
def get_element_length(element_number, beams_information):
    """Finds the length of an element.
    
    Arguments:
        element_number    -- the number of the element
        beams_information -- a list containing for each beam its main information:
                             beam length, beam orientation, number of elements 
                             created on the beam, length of these elements
        
    Return values:
        element_length -- the length of the element
    """
    #Find the elements beam number
    element_counter=0
    for i in range(len(beams_information)):
        if (element_number>=element_counter 
            and element_number<=element_counter+beams_information[i][2]-1):
            beam_nr = i
            break
        else:
            element_counter+=beams_information[i][2]
    
    #Get the element length with the beam number
    element_length=beams_information[beam_nr][3]
        
    return element_length
 
def include_hinges(assembled_force_vector, element_length, release_start,
                   release_end):
    """Creates a copy of the assembled force vector to take into account the hinges.
    
    Arguments:
        assembled_force_vector -- the nodal force vector of one assembled 
                                  loaded element (not including any hinges)
        element_length         -- the length of the beams elements
        release_start          -- the type of the release at the start of the 
                                  element
        release_end            -- the type of the release at the end of the 
                                  element
    
    Return values:
        local_force_vector -- the nodal force vector of one assembled loaded
                              element (including hinges)
    """
    
    local_force_vector = deepcopy(assembled_force_vector)
    
    forces = assembled_force_vector
    
    if release_start==1 and release_end==1:
        local_force_vector[1] = forces[1]-1/element_length*(forces[2]+forces[5])
        local_force_vector[2] = 0
        local_force_vector[4] = forces[4]+1/element_length*(forces[2]+forces[5])
        local_force_vector[5] = 0
    elif release_start==1:
        local_force_vector[1] = forces[1]-3/(2*element_length)*(forces[2])
        local_force_vector[2] = 0
        local_force_vector[4] = forces[4]+3/(2*element_length)*(forces[2])
        local_force_vector[5] = forces[5]-1/2*(forces[2])
    elif release_end==1:
        local_force_vector[1]=forces[1]-3/(2*element_length)*(forces[5])
        local_force_vector[2]=forces[2]-1/2*(forces[5])
        local_force_vector[4]=forces[4]+3/(2*element_length)*(forces[5])
        local_force_vector[5]=0
    
    return local_force_vector