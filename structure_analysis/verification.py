# -*- coding: utf-8 -*-
"""
Created on Mon May 27 16:55:34 2019

@author: umorf

This module contains the function which verifies the model. It raises Warnings
(Errors) for critical issues, whereas it modifies the model for non-critical
issues and provides some input features.
"""

import warnings
from copy import deepcopy

import numpy as np


def verify_input(model_original):
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

        Multiple initial displacements of the same node in the same load group are merged.
    """
    model = deepcopy(model_original)
    # Get the models information. Create an empty releases list if it was not specified.
    nodes = model['Nodes']['Location']
    beams_nodes = model['Beams']['Nodes']
    beams_stiffness = model['Beams']['Stiffness']
    loads = model['Loads']
    if 'Releases' not in model['Beams']:
        model['Beams']['Releases'] = []
    if 'Rotated Degrees' not in model['Boundary Conditions']:
        model['Boundary Conditions']['Rotated Degrees'] = []
    if 'Restricted Degrees' not in model['Boundary Conditions']:
        model['Boundary Conditions']['Restricted Degrees'] = []
    if 'Springs' not in model['Boundary Conditions']:
        model['Boundary Conditions']['Springs'] = []
    beams_releases = model['Beams']['Releases']
    rotated_degrees = model['Boundary Conditions']['Rotated Degrees']
    restricted_degrees = model['Boundary Conditions']['Restricted Degrees']
    springs = model['Boundary Conditions']['Springs']

    # Convert to integer values in case floats were given
    for beam_nodes in beams_nodes:
        beam_nodes[0] = int(beam_nodes[0])
        beam_nodes[1] = int(beam_nodes[1])
    for beam_releases in beams_releases:
        beam_releases[0] = int(beam_releases[0])
    for load_group in loads:
        if 'Nodal' in load_group and load_group['Nodal']:
            for nodal_load in load_group['Nodal']:
                nodal_load[0] = int(nodal_load[0])
        if 'Point' in load_group and load_group['Point']:
            for point_load in load_group['Point']:
                point_load[0] = int(point_load[0])
        if 'Distributed' in load_group and load_group['Distributed']:
            for distributed_load in load_group['Distributed']:
                distributed_load[0] = int(distributed_load[0])
        if 'Functions' in load_group and load_group['Functions']:
            for load_function in load_group['Functions']:
                load_function[0] = int(load_function[0])
        if 'Initial Displacements' in load_group and load_group['Initial Displacements']:
            for initial_displacement in load_group['Initial Displacements']:
                initial_displacement[0] = int(initial_displacement[0])
    for restricted_degree in restricted_degrees:
        restricted_degree[0] = int(restricted_degree[0])
        restricted_degree[1] = int(restricted_degree[1])
        restricted_degree[2] = int(restricted_degree[2])
        restricted_degree[3] = int(restricted_degree[3])

    # Check whether all beams_nodes actually exist.
    max_beam_node = max([max(beam_nodes[0], beam_nodes[1]) for beam_nodes in beams_nodes])
    if max_beam_node > len(nodes) - 1:  # or bool(min_beamnode):
        raise Exception('Some beams reference nodes which are not defined.')

    # Check whether the the lenths of the input are coherent.
    if len(beams_stiffness) != len(beams_nodes):
        raise Exception('BeamsNodes and BeamsStiffness are of different size.')

    # Check whether the normal and bending stiffness are equal to zero
    for beam_stiffness in beams_stiffness:
        if beam_stiffness[0] == 0:
            raise Exception('The normal stiffness cannot be zero.')
        if beam_stiffness[1] == 0:
            raise Exception('The bending stiffness cannot be zero, even on pendulum beams.')

    # Check whether there are unused nodes
    unused_nodes = []
    for i in range(len(nodes)):
        is_used = any([nodes[0] == i or nodes[1] == i for nodes in beams_nodes])
        if not is_used:
            # raise Exception('There are unused nodes.')
            unused_nodes.append(i)

    # delete or modify any other input which is related to it
    if unused_nodes:
        counter = 0
        nodes_adapt_dict = {}
        for i in range(len(nodes)):
            if i in unused_nodes:
                counter += 1
            nodes_adapt_dict[i] = i-counter

        unused_nodes.sort(reverse=True)
        for i in unused_nodes:
            nodes.pop(i)

        for beam_nodes in beams_nodes:
            beam_nodes[0] = nodes_adapt_dict[beam_nodes[0]]
            beam_nodes[1] = nodes_adapt_dict[beam_nodes[1]]
        for load_group in loads:
            if 'Nodal' in load_group and load_group['Nodal']:
                for nodal_load in load_group['Nodal']:
                    nodal_load[0] = nodes_adapt_dict[nodal_load[0]]
            if 'Initial Displacements' in load_group and load_group['Initial Displacements']:
                for initial_displacement in load_group['Initial Displacements']:
                    initial_displacement[0] = nodes_adapt_dict[initial_displacement[0]]
        for rotated_degree in rotated_degrees:
            rotated_degree[0] = nodes_adapt_dict[rotated_degree[0]]
        for restricted_degree in restricted_degrees:
            restricted_degree[0] = nodes_adapt_dict[restricted_degree[0]]
        for spring in springs:
            spring[0] = nodes_adapt_dict[spring[0]]

    # Modify the loads.
    beam_information = get_beams_length_angle(nodes, beams_nodes)
    for load_group in loads:

        # Modify the point loads
        point_loads_todelete = []
        if 'Point' in load_group and load_group['Point']:
            for point_load_nr, point_load in enumerate(load_group['Point'], 0):

                # If located at the beginning or end of a beam, they are converted to nodal loads
                if point_load[1] == 0:
                    start_node = beams_nodes[point_load[0]][0]
                    if 'Nodal' not in load_group:
                        load_group['Nodal'] = []
                    load_group['Nodal'].append([start_node, point_load[2], point_load[3], point_load[4]])
                    point_loads_todelete.append(point_load_nr)
                if np.isclose(point_load[1], beam_information[point_load[0]][0]):
                    end_node = beams_nodes[point_load[0]][1]
                    if 'Nodal' not in load_group:
                        load_group['Nodal'] = []
                    load_group['Nodal'].append([end_node, point_load[2], point_load[3], point_load[4]])
                    point_loads_todelete.append(point_load_nr)
                if point_load[1] < 0:
                    point_load[1] += beam_information[point_load[0]][0]
                if point_load[1] < 0 or point_load[1] > beam_information[point_load[0]][0] * 1.0001:
                    raise Exception('A point load is invalid because its position is not located on the beam.')

            # Delete the modified points loads.
            point_loads_todelete.sort(reverse=True)
            for i in point_loads_todelete:
                load_group['Point'].pop(i)

        # Modify the distributed loads
        if 'Distributed' in load_group and load_group['Distributed']:
            for line_load in load_group['Distributed']:
                if line_load[1] < 0:
                    line_load[1] += beam_information[line_load[0]][0]
                if line_load[2] <= 0:
                    line_load[2] += beam_information[line_load[0]][0]
                if line_load[1] > line_load[2]:
                    line_load[1], line_load[2] = line_load[2], line_load[1]
                    line_load[3], line_load[6] = line_load[6], line_load[3]
                    line_load[4], line_load[7] = line_load[7], line_load[4]
                    line_load[5], line_load[8] = line_load[8], line_load[5]
                    warnings.warn('A distributed load was entered end to start.')
                if line_load[1] < 0 or line_load[2] > beam_information[line_load[0]][0] * 1.0001:
                    raise Exception('A distributed load exceeds its beam.')

        # Modify the functional loads
        if 'Functions' in load_group and load_group['Functions']:
            for load_function in load_group['Functions']:
                if load_function[1] < 0:
                    load_function[1] += beam_information[load_function[0]][0]
                if load_function[2] <= 0:
                    load_function[2] += beam_information[load_function[0]][0]
                if load_function[1] > load_function[2]:
                    load_function[1], load_function[2] = load_function[2], load_function[1]
                    warnings.warn('A functional load was entered end to start.')
                if (load_function[1] < 0 or
                        load_function[2] > beam_information[load_function[0]][0] * 1.0001):
                    raise Exception('A functional load exceeds its beam.')

    # Check whether some nodes are connected to nothing but releases.
    released_nodes = []
    for i in range(len(nodes)):
        # Count how many times the node is used in a beam:
        times_used = sum([nodes[0] == i or nodes[1] == i for nodes in beams_nodes])

        times_released = sum([((beams_nodes[release[0]][0] == i and release[1] == 1) or
                               (beams_nodes[release[0]][1] == i and release[2] == 1))
                              for release in beams_releases])
        if times_used == times_released:
            released_nodes.append(i)
    if released_nodes:
        for released_node in released_nodes:
            for release in beams_releases:
                if beams_nodes[release[0]][0] == released_node and release[1] == 1:
                    release[1] = 0
                    break
                if beams_nodes[release[0]][1] == released_node and release[2] == 1:
                    release[2] = 0
                    break
        warnings.warn('Each node needs at least one beam with a clamped release.'
                      'The following nodes releases were altered: ' + str(released_nodes), Warning)

    # Check whether some nodes were restricted more than once.
    multiple_restrictions = []
    multiple_restricted_nodes = []
    for i in range(len(restricted_degrees)):
        for j in range(i):
            if restricted_degrees[i][0] == restricted_degrees[j][0]:
                restricted_degrees[j][1] = max(restricted_degrees[j][1],
                                               restricted_degrees[i][1])
                restricted_degrees[j][2] = max(restricted_degrees[j][2],
                                               restricted_degrees[i][2])
                restricted_degrees[j][3] = max(restricted_degrees[j][3],
                                               restricted_degrees[i][3])
                multiple_restricted_nodes.append((j, i))
                multiple_restrictions.append(i)
                break
    if multiple_restrictions:
        multiple_restrictions.sort(reverse=True)
        for i in multiple_restrictions:
            restricted_degrees.pop(i)
        # warnings.warn('The following restricted degrees were merged, because their nodes'
        #               'are the same: ' + str(multiple_restricted_nodes), Warning)

    # Check whether one node has more than one initial displacement in the same loadgroup.
    for load_group in loads:
        multiple_displacements = []
        if 'Initial Displacements' in load_group and load_group['Initial Displacements']:
            for id_nr, initial_displacement in enumerate(load_group['Initial Displacements'], 0):
                for j in range(id_nr):
                    if initial_displacement[0] == load_group['Initial Displacements'][j][0]:
                        load_group['Initial Displacements'][j][1] += initial_displacement[1]
                        load_group['Initial Displacements'][j][2] += initial_displacement[2]
                        load_group['Initial Displacements'][j][3] += initial_displacement[3]
                        multiple_displacements.append(id_nr)
                        break

        if multiple_displacements:
            multiple_displacements.sort(reverse=True)
            for i in multiple_displacements:
                load_group['Initial Displacements'].pop(i)

    # # Check whether the system is kinematically stable. Define discElements as 1
    # # and check whether the stiffness matrix is regular.
    # discretization_information = discretize(model['Nodes'], model['Beams'], discType='Elementwise', discElements=1)
    # nodes_lists = discretization_information['Nodes']
    # releases_beams = discretization_information['Releases']['Beams']
    # beams_information = discretization_information['Beams Information']
    #
    # stiffness_mat = get_stiffness_matrix(beams_stiffness, nodes_lists, releases_beams, beams_information)
    # force_mat = np.ones((len(nodes) * 3, 1))
    # modified_matrices = apply_boundary_conditions(model['Boundary Conditions'], stiffness_mat, force_mat)
    # if modified_matrices[0].shape[0] != 0:
    #     rank = np.linalg.matrix_rank(modified_matrices[0].toarray())
    #     n_dofs = modified_matrices[0].shape[0]
    #     if rank != n_dofs:
    #         print("The rank is not full! Number of dofs:" + str(n_dofs))
    #         # raise Exception('The system is kinematically unstable.')

    return model


def get_beams_length_angle(nodes, beams_nodes):
    """Calculates each beams length and angle.

    Arguments:
        nodes       -- the list of the original (not discretized) nodes position
        beams_nodes -- the list of the beams starting and ending nodes

    Return values:
        beams_length_angle -- a list containing for each beam its length and orientation
    """
    beams_length_angle = []

    # Append the list for each beam
    for beam_nodes in beams_nodes:

        start_node = beam_nodes[0]
        end_node = beam_nodes[1]

        # Calculate the distance in each direction.
        dx = nodes[end_node][0] - nodes[start_node][0]
        dz = nodes[end_node][1] - nodes[start_node][1]

        # Calculate the length.
        length = (dx ** 2 + dz ** 2) ** 0.5

        # Calculate the orientation.
        if dx == 0:
            if dz >= 0:
                angle = np.pi / 2
            else:
                angle = -np.pi / 2
        else:
            angle = np.arctan(dz / dx)
            if dx < 0:
                if dz > 0:
                    angle += np.pi
                else:
                    angle -= np.pi

        beams_length_angle.append([length, angle, 1, length])

    return beams_length_angle
