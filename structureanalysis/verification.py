# -*- coding: utf-8 -*-
"""
Created on Mon May 27 16:55:34 2019

@author: umorf

This module contains the function which veryfies the model. It raises Warnings 
(Errors) for critcial issues, whereas it modifes the model for noncritical 
issues and provides some input features.
"""

import numpy as np
import warnings
from .discretization import discretize
from .assembly.stiffness_matrix import get_stiffness_matrix
from .apply_boundary_conditions import apply_boundary_conditions

def verify_input(model):
    """Checks whether the model is valid and modifies certain mistakes.
    
    The function raises warnings if:
        BeamsNodes reference nodes which do not exist
        
        BeamsNodes and BeamsStiffness are not of the same length
        
        The normal stiffness is not zero
        
        The bending stiffness is not zero
        
        The loads positions exceed their beams
        
        The system is kinematically unstable
        
    
    The function modifies:
        All beam and node indexes are converted to integers
        
        Nodes that are restricted multiple times are merged
        
        Point loads that are at the very start or end of the beam are converted
        to nodal loads (They do not appear in the internal forces of the first/
        last point on the element)
        
        If the start is bigger than the ending location of a load, they are switched
        
        Negative positions of loads are treated as distance from the ending node
        
        If the ending position is zero, it's modified to the end of the beam
        
        Unused nodes (not connected to any beam) are deleted including their 
        restricted degrees, initial displacements and nodal loads
        
        At nodes that are connected to hinged beams only, one release is 
        modified to be clamped (needed for the calculations, doesn't change the
        result)
        
        Multiple initial displacements of the same node in the same loadgroup 
        are merged.
    """
    #Get the models information. Create an empty releases list if it wasnt specified.
    nodes=model['Nodes']['Location']
    beams_nodes=model['Beams']['Nodes']
    beamsstiffness=model['Beams']['Stiffness']
    if 'Releases' not in model['Beams']:
        model['Beams']['Releases']=[]
    beamsreleases = model['Beams']['Releases']
    loads=model['Loads']
    restricted_degrees=model['Boundary Conditions']['Restricted Degrees']
    
    #Convert to integer values in case floats were given
    for beamsnode in beams_nodes:
        beamsnode[0]=int(beamsnode[0])
        beamsnode[1]=int(beamsnode[1])
    for beamsrelease in beamsreleases:
        beamsrelease[0]=int(beamsrelease[0])
    for loadgroup in loads:
        if 'Nodal' in loadgroup and loadgroup['Nodal']:
            for nodal_load in loadgroup['Nodal']:
                nodal_load[0]=int(nodal_load[0])
        if 'Point' in loadgroup and loadgroup['Point']:
            for point_load in loadgroup['Point']:
                point_load[0]=int(point_load[0])
        if 'Distributed' in loadgroup and loadgroup['Distributed']:
            for distributed_load in loadgroup['Distributed']:
                distributed_load[0]=int(distributed_load[0])
        if 'Functions' in loadgroup and loadgroup['Functions']:
            for load_function in loadgroup['Functions']:
                load_function[0]=int(load_function[0])
        if 'Initial Displacements' in loadgroup and loadgroup['Initial Displacements']:
            for initial_displacement in loadgroup['Initial Displacements']:
                initial_displacement[0]=int(initial_displacement[0])       
    for restricted_degree in restricted_degrees:
        restricted_degree[0]=int(restricted_degree[0])
        restricted_degree[1]=int(restricted_degree[1])
        restricted_degree[2]=int(restricted_degree[2])
        restricted_degree[3]=int(restricted_degree[3])
    
    #Check whether all beamsnodes actually exist.
    min_beamnode=min([min(beamnodes[0],beamnodes[1]) for beamnodes in beams_nodes])
    max_beamnode=max([max(beamnodes[0],beamnodes[1]) for beamnodes in beams_nodes])
    if bool(min_beamnode) or max_beamnode>len(nodes)-1:
        raise Exception('Some beams reference nodes which are not defined.')
        
    #Check whether the the lenths of the input are coherent.
    if len(beamsstiffness)!=len(beams_nodes):
        raise Exception('BeamsNodes and BeamsStiffness are of different length.')

    #Check whether the normal and bending stiffness are equal to zero
    for beamstiffness in beamsstiffness:
        if beamstiffness[0]==0:
            raise Exception('The normal stiffness cannot be zero.')
        if beamstiffness[1]==0:
            raise Exception('The bending stiffnes cannot be zero, even on pendulum beams.')
            
            
    
    #Check whether there are unused nodes and delete or modify any other input
    # which is related to it.
#    unused_nodes=[]
    for i in range(len(nodes)):
        is_used=any([nodes[0]==i or nodes[1]==i for nodes in beams_nodes])
        if not is_used:
            raise Exception('There are unused nodes.')
#            unused_nodes.append(i)
#    if unused_nodes!=[]:
#        counter=-1
#        warnings.warn('The following nodes were deleted because they were unsused: '
#                      +str(unused_nodes), Warning)
#        for unused_node in unused_nodes:
#            counter+=1
#            nodes.pop(unused_node-counter)
#            for beamnodes in beams_nodes:
#                if beamnodes[0]>unused_node-counter:
#                    beamnodes[0]-=1
#                if beamnodes[1]>unused_node-counter:
#                    beamnodes[1]-=1
#            for loadgroup in loads:
#                if 'Nodal' in loadgroup and loadgroup['Nodal']:
#                    for nodal_load in loadgroup['Nodal']:
#                        if nodal_load[0]==unused_node-counter:
#                            del(nodal_load)
#                            warnings.warn('A nodal load was deleted because it '
#                                          +'was located on an unused node.', Warning)
#                        if nodal_load[0]>unused_node-counter:
#                            nodal_load[0]-=1
#                if 'Initial Displacements' in loadgroup and loadgroup['Initial Displacements']:
#                    for initial_displacement in loadgroup['Initial Displacements']:
#                        if initial_displacement[0]==unused_node-counter:
#                            del(initial_displacement)
#                            warnings.warn('An initial displacement was deleted because '
#                                          +'it was located on an unused node.', Warning)
#                        if initial_displacement[0]>unused_node-counter:
#                            initial_displacement[0]-=1
#            for restricted_degree in restricted_degrees:
#                if restricted_degree[0]>unused_node-counter:
#                    restricted_degree[0]-=1
#                if restricted_degree[0]==unused_node-counter:
#                    del(restricted_degree)
#                    warnings.warn('A restricted degree was deleted because it was '
#                                  +'located on an unused node.', Warning)
    
    #Modify the loads.
    beaminformation=get_beams_length_angle(nodes, beams_nodes)
    for loadgroup in loads:
        
        #Modify the point loads
        point_loads_todelete=[]
        if 'Point' in loadgroup and loadgroup['Point']:
            for point_load_nr, point_load in enumerate(loadgroup['Point'],0):
                
                #If located at the beginning or end of a beam, they are 
                # converted to nodal loads
                if point_load[1]==0:
                    startnode=beams_nodes[point_load[0]][0]
                    if 'Nodal' not in loadgroup:
                        loadgroup['Nodal']=[]
                    loadgroup['Nodal'].append([startnode,point_load[2],
                                              point_load[3],point_load[4]])
                    point_loads_todelete.append(point_load_nr)
                if np.isclose(point_load[1],beaminformation[point_load[0]][0]):
                    endnode=beams_nodes[point_load[0]][1]
                    if 'Nodal' not in loadgroup:
                        loadgroup['Nodal']=[]
                    loadgroup['Nodal'].append([endnode,point_load[2],point_load[3],
                                              point_load[4]])
                    point_loads_todelete.append(point_load_nr)
                if point_load[1]<0:
                    point_load[1]+=beaminformation[point_load[0]][0]
                if (point_load[1]<0 or 
                    point_load[1]>beaminformation[point_load[0]][0]*1.0001):
                    raise Exception('A point load is invalid because its position '
                                  +'is not located on the beam.')
            
            #Delete the modified points loads.
            counter=-1
            for i in point_loads_todelete:
                counter+=1
                loadgroup['Point'].pop(i-counter)
        
        #Modify the distributed loads
        if 'Distributed' in loadgroup and loadgroup['Distributed']:
            for line_load in loadgroup['Distributed']:
                if line_load[1]<0:
                    line_load[1]+=beaminformation[line_load[0]][0]
                if line_load[2]<=0:
                    line_load[2]+=beaminformation[line_load[0]][0]
                if line_load[1]>line_load[2]:
                    line_load[1],line_load[2] = line_load[2],line_load[1]
                    line_load[3],line_load[6] = line_load[6],line_load[3]
                    line_load[4],line_load[7] = line_load[7],line_load[4]
                    line_load[5],line_load[8] = line_load[8],line_load[5]
                    warnings.warn('A distributed load was entered end to start.')
                if line_load[1]<0 or line_load[2]>beaminformation[line_load[0]][0]*1.0001:
                    raise Exception('A distributed load exceeds its beam.')
                    
        #Modify the functional loads
        if 'Functions' in loadgroup and loadgroup['Functions']:
            for load_function in loadgroup['Functions']:
                if load_function[1]<0:
                    load_function[1]+=beaminformation[load_function[0]][0]
                if load_function[2]<=0:
                    load_function[2]+=beaminformation[load_function[0]][0]
                if load_function[1]>load_function[2]:
                    load_function[1],load_function[2]= load_function[2],load_function[1]
                    warnings.warn('A functional load was entered end to start.')
                if (load_function[1]<0 or 
                    load_function[2]>beaminformation[load_function[0]][0]*1.0001):
                    raise Exception('A functional load exceeds its beam.')
    
    #Check whether some nodes are connected to nothing but releases.
    released_nodes=[]
    for i in range(len(nodes)):
        #Count how many times the node is used in a beam:
        times_used=sum([nodes[0]==i or nodes[1]==i for nodes in beams_nodes])
        
        times_released=sum([((beams_nodes[release[0]][0]==i and release[1]==1) or 
                             (beams_nodes[release[0]][1]==i and release[2]==1)) 
                              for release in beamsreleases])
        if times_used==times_released:
            released_nodes.append(i)
    if released_nodes!=[]:
        for released_node in released_nodes:
            for release in beamsreleases:
                if (beams_nodes[release[0]][0]==released_node and release[1]==1):
                    release[1]=0
                    break
                if (beams_nodes[release[0]][1]==released_node and release[2]==1):
                    release[2]=0
                    break
        warnings.warn('Each node needs at least one beam with a clamped release.'
                      'The following nodes releases were altered: '
                      +str(released_nodes), Warning)
    
    #Check whether some nodes were restricted more than once.
    multiple_restrictions=[]
    multiple_restricted_nodes=[]
    for i in range(len(restricted_degrees)):
        for j in range(i):
            if restricted_degrees[i][0]==restricted_degrees[j][0]:
                restricted_degrees[j][1]=max(restricted_degrees[j][1],
                                             restricted_degrees[i][1])
                restricted_degrees[j][2]=max(restricted_degrees[j][2],
                                             restricted_degrees[i][2])
                restricted_degrees[j][3]=max(restricted_degrees[j][3],
                                             restricted_degrees[i][3])
                multiple_restricted_nodes.append((j,i))
                restricted_degrees[i][0]=-1
                multiple_restrictions.append(i)
                break
    if multiple_restrictions!=[]:
        counter=0
        for i in range(len(multiple_restrictions)):
            restricted_degrees.pop(multiple_restrictions[i]-counter)
            counter+=1
        warnings.warn('The following restricted degrees were merged, because their nodes'
                      'are the same: '+str(multiple_restricted_nodes), Warning)
        
        
    #Check whether one node has more than one initial displacement in the same loadgroup.
    for loadgroup in loads:
        multiple_displacements=[]
        if 'Initial Displacements' in loadgroup and loadgroup['Initial Displacements']:
            for id_nr, initial_displacement in enumerate(loadgroup['Initial Displacements'],0):
                for j in range(id_nr):
                    if initial_displacement[0]==loadgroup['Initial Displacements'][j][0]:
                        loadgroup['Initial Displacements'][j][1]+=initial_displacement[1]
                        loadgroup['Initial Displacements'][j][2]+=initial_displacement[2]
                        loadgroup['Initial Displacements'][j][3]+=initial_displacement[3]
                        multiple_displacements.append(id_nr)
                        break

        if multiple_displacements!=[]:
            counter=0
            for i in range(len(multiple_displacements)):
                loadgroup['Initial Displacements'].pop(multiple_displacements[i]-counter)
                counter+=1
    
    #Check whether the system is kinematically stable. Define discElements as 1
    # and check whether the stiffness matrix is regular.
    discretization_information = discretize(model['Nodes'], model['Beams'], 
                                            discType='Elementwise',
                                            discElements=1)
    nodes_lists         = discretization_information['Nodes']
    releases_beams      = discretization_information['Releases']['Beams']
    beams_information   = discretization_information['Beams Information']
    
    stiffness_mat = get_stiffness_matrix(beamsstiffness, nodes_lists,
                                         releases_beams, beams_information)
    force_mat=np.ones((len(nodes)*3,1))
    modified_matrices = apply_boundary_conditions(model['Boundary Conditions'],
                                                  stiffness_mat, force_mat)
    if modified_matrices[0].shape[0] !=0:
        rank=np.linalg.matrix_rank(modified_matrices[0].toarray())
        ndofs=modified_matrices[0].shape[0]
        if rank!=ndofs:
            raise Exception('The system is kinematically unstable.')
                
    return


def get_beams_length_angle(nodes, beams_nodes):
    """Calculates each beams length and angle.
    
    Arguments:
        nodes       -- the list of the original (not discretized) nodes position
        beams_nodes -- the list of the beams starting and ending nodes
        
    Return values:
        beams_length_angle -- a list containing for each beam its length and orientation
    """
    beams_length_angle=[]
    
    #Append the list for each beam
    for beamnodes in beams_nodes:
        
        start_node=beamnodes[0]
        end_node=beamnodes[1]
        
        #Calculate the distance in each direction.
        dx=nodes[end_node][0]-nodes[start_node][0]
        dz=nodes[end_node][1]-nodes[start_node][1]
        
        #Calculate the length.
        length=((dx)**2+(dz)**2)**0.5
        
        #Calculate the orientation.
        if dx==0:
            if dz>=0:
                angle=np.pi/2               
            else:
                angle=-np.pi/2
        else:
            angle=np.arctan((dz)/(dx))
            if dx<0:
                if dz>0:
                    angle+=np.pi
                else:
                    angle-=np.pi
                    
        beams_length_angle.append([length, angle, 1, length])
       
    return beams_length_angle