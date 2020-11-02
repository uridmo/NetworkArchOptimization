# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 15:28:12 2019

@author: umorf

This module contains all the functions for discretizing the system, including
its main function discretize().

The information of the discretization is stored in a dictionary containing
the following keys:
    'Nodes'              -- a list containing for each beam an ordered
                            list of the node numbers along the beam
    'Beams Information'  -- a list containing for each beam its main
                            information: beam length, beam orientation,
                            number of elements created on the beam, length
                            of these elements
    'Elements'           -- a list containing for each beam a list of the
                            elements on the beam in consecutive order
    'Releases'           -- a dictionary with the keys 'Beams' and 
                            'Elements' containing for each a dictionary
                            containing the hinged releases to the according 
                            element or beam numbers
"""

import numpy as np

def discretize(nodes, beams, discType='Elementwise', discElements=100, discLength=0.1):
    """Creates the information of the discretized system.
    
    Every beam is divided into smaller elements of equal length (per beam).
    
    The method of the discretization of the system is controlled by the keyword
    arguments.

    Arguments:
        nodes -- a dictionary containing all the model's information on the nodes 
        beams -- a dictionary containing all the model's information on the beams 
        
    Keyword arguments:
        discType     -- describes the method of discretizing the beams. Either 
                        'Elementwise' or 'Lengthwise' 
        discElements -- the amount of elements each beam is subdivided into if 
                        discType is 'Elementwise'
        disclength   -- the length of the beams elements the maximal length of 
                        the elements each beam is subdivided into if discType 
                        is 'Lengthwise'
    
    Return values:
        discretization_information -- the dictionary containing the information
                                      of the discretized system

    """
    #Get the required information from the input.
    nodes_location  = nodes['Location']
    beams_nodes     = beams['Nodes']
    
    #Move to an input correction function.
    if 'Releases' in beams:
        beams_releases  = beams['Releases']
    else:
        beams_releases = []
    
    #Create the necessary information about the discretized model.
    beams_information = get_beams_information(nodes_location, beams_nodes,
                                              discType, discElements, discLength)
    
    nodes_lists = generate_nodes(nodes_location, beams_nodes, beams_information)
    
    elements_lists = enumerate_beam_element(nodes_lists)
    
    releases = get_releases_lists(beams_nodes, beams_releases, elements_lists)
    
    #Create the output dictionary containing the created information.
    discretization_information={'Nodes'             :nodes_lists,
                                'Beams Information' :beams_information,
                                'Elements'          :elements_lists,
                                'Releases'          :releases}
    
    return discretization_information


def get_beams_information(nodes_location, beams_nodes, discType='Elementwise',
                          discElements=100, discLength=0.1):
    """Calculates the main information of the discretized beams and its elements.
    
    The method of the discretization of the system is controlled by the keyword
    arguments.
    
    Arguments:
        nodes_location -- the list of the original (not discretized) nodes 
                          position 
        beams_nodes    -- the list of the beams starting and ending nodes a 
                          dictionary containing all the model's information on 
                          the nodes 
        
    Keyword arguments:
        discType     -- describes the method of discretizing the beams. Either 
                        'Elementwise' or 'Lengthwise' 
        discElements -- the amount of elements each beam is subdivided into if 
                        discType is 'Elementwise'
        disclength   -- the length of the beams elements the maximal length of 
                        the elements each beam is subdivided into if discType 
                        is 'Lengthwise'
                        
    Return values:
        beams_information -- a list containing for each beam its main 
                             information: beam length, beam orientation, number
                             of elements created on the beam, length of these 
                             elements 
    """
    beams_information=[]
    # Expand the list with a list containing the information of each beam.
    for beam_nodes in beams_nodes:
        
        start_node=beam_nodes[0]
        end_node=beam_nodes[1]
        
        #Calculate the distance in each direction.
        dx=nodes_location[end_node][0]-nodes_location[start_node][0]
        dz=nodes_location[end_node][1]-nodes_location[start_node][1]
        
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
        
        #Calculate the number of elements on the beam.
        if discType is 'Elementwise':
            number_of_elements = discElements
        elif discType is 'Lengthwise':
            number_of_elements = int(np.ceil(length/discLength))
        
        #Calculate the length of each element.
        element_length=length/(number_of_elements)
        
        #Append the list with the information of the current beam 
        beams_information.append([length,angle,number_of_elements,element_length])
            
    return beams_information


def generate_nodes(nodes_location, beams_nodes, beams_information):
    """Creates a list containing for each beam an ordered list of its nodes.
    
    Arguments:
        nodes_location    -- the list of the original (not discretized) nodes 
                             position
        beams_nodes       -- the list of the beams starting and ending nodes a 
                             dictionary containing all the model's information 
                             on the nodes
        beams_information -- a list containing for each beam its main 
                             information: beam length, beam orientation, number
                             of elements created on the beam, length of these 
                             elements
    
    Return values:
        nodes_lists -- a list containing for each beam an ordered list of the 
                       node numbers along the beam
    """
    #Get the number of original nodes.
    number_of_nodes=len(nodes_location)
    
    nodes_lists=[]
    #Expand the list with the nodes list of each beam.
    for beam_number, beam_nodes in enumerate(beams_nodes, 0):
        start_node=beam_nodes[0]
        end_node=beam_nodes[1]
        
        #Determine number of nodestoadd of the current beam.
        nodes_toadd=beams_information[beam_number][2]-1
        
        #Create the ordered list of the nodes of the current beam.
        nodes_list_toadd=list(range(number_of_nodes, number_of_nodes+nodes_toadd))
        nodes_list_toadd.append(end_node)
        nodes_list_toadd.insert(0, start_node)
        
        #Update the number of nodes.
        number_of_nodes+=nodes_toadd
        
        #Append the list with the nodes of the current beam
        nodes_lists.append(nodes_list_toadd)
        
    return nodes_lists


def enumerate_beam_element(nodes_lists):
    """Creates a list containing for each beam an ordered list of its elements.
    
    Arguments:
        nodes_lists -- a list containing for each beam an ordered list of the 
                       node numbers along the beam
    
    Return values:
        elements_lists -- a list containing for each beam a list of the elements
                          on the beam in consecutive order 
    """
    number_of_elements=0
    elements_lists=[]
    #Expand the list and the number with the elements list of each beam.
    for nodes_list in nodes_lists:
        #Get the number of nodes on each beam.
        number_of_elements_toadd=len(nodes_list)-1
        
        #Update the List and the total number accordingly.
        new_number_of_elements = number_of_elements + number_of_elements_toadd
        elements_lists.append(list(range(number_of_elements,
                                         new_number_of_elements)))
        number_of_elements = new_number_of_elements
        
    return elements_lists


def get_releases_lists(beams_nodes, beams_releases, elements_lists):
    """Saves the input relases to their according beam and element numbers.
    
    As output a dictionary with the keys 'Beams' and 'Elements' is used. Each 
    containg another dictionary saving, for the special elements, the
    releases at its start and end.
    
    Arguments:
        beams_nodes    -- the list of the beams starting and ending nodes a 
                          dictionary containing all the model's information on 
                          the nodes
        beams_releases -- a dictionary with the keys 'Beams' and 'Elements' 
                          containing for each a dictionary containing the hinged
                          releases to the according element or beam numbers a 
                          list containing information on the beams releases
        elements_lists -- a list containing for each beam a list of the elements
                          on the beam in consecutive order
    
    Return values:
        releases -- a dictionary with the keys 'Beams' and 'Elements' containing
                    for each a dictionary containing the hinged releases to the
                    according element or beam numbers 
    """

    #Create the empty release dictinaries.
    releases_beams={}
    releases_elements={}

    
    #Expand the dictionaries with the systems actual releases
    for release in beams_releases:
        beam_nr         = release[0]
        release_start   = release[1]
        release_end     = release[2]
        
        element_nr_start = elements_lists[beam_nr][0]
        element_nr_end   = elements_lists[beam_nr][-1]
        
        releases_beams[beam_nr] = [release_start, release_end]
        
        if element_nr_start == element_nr_end:
            releases_elements[element_nr_start] = [release_start, release_end]
        else:
            if release_start == 1:
                releases_elements[element_nr_start] = [1, 0]
            if release_end == 1:
                releases_elements[element_nr_end] = [0, 1]
         
    releases={'Beams':releases_beams, 'Elements':releases_elements}
    
    return releases