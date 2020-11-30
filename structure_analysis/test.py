import numpy as np

from structure_analysis import structure_analysis

h = 10
l = 15

# NODES

# The nodes positions are stored in a dictionary with the key "Location". They
# are stored in lists containing the x- and y-coordinate of each node. The node 
# numbers correspond to the order of the list. (starting from zero)
nodes_position = [[0, 0],
                  [0, h],
                  [l, h],
                  [l, 0]]
nodes = {'Location': nodes_position}

# BEAMS

# The information of the beams is stored in a dictionary with the keys 'Nodes'
# and 'Stiffness'. Also the beam numbers correspond the the order of the lists.
# (The optional shear stiffness and end releases are left away for simplicity.)

# The beams nodes are described using the starting and the ending node number of
# each beam.
beams_nodes = [[0, 1],
               [1, 2],
               [2, 3]]
# The beams stiffnesses are stored in a list containing for each beam its normal
# and bending stiffness.
beams_stiffness = [[5.700 * 10 ** 5, 3.886 * 10 ** 3],  # IPE 200
                   [1.076 * 10 ** 6, 1.671 * 10 ** 4],  # IPE 300
                   [5.700 * 10 ** 5, 3.886 * 10 ** 3]]  # IPE 200

beams = {'Nodes': beams_nodes, 'Stiffness': beams_stiffness}

# LOADS

# The loads are stored in a list with a dictionary for each loadgroup. Four of
# the five different loadtypes are used in this example, assigned to different
# loadgroups. (Functional Loads are left away for simplicity)

# The loadtype 'Point' is used to describe concentrated forces that are applied
# on beams:
#                        [BeamNr,  Position,   Fx,   Fy,   Mz]
load_point = [[1, l / 2, 0, -10, 0]]

# The loadtype 'Distributed' is used to describe linearly distributed forces:
#                      [BeamNr, StartPos, EndPos, qxStart, qyStart, mzStart, qxEnd, qyEnd, mzEnd]
load_distributed = [[1, 0, 0, 0, -2, 0, 0, -2, 0]]

# Assignment to the different loadgroups.
loadgroup1 = {'Point': load_point}
loadgroup2 = {'Distributed': load_distributed}

# Definition of the loads variable.
loads = [loadgroup1, loadgroup2]

# BOUNDARY CONDITIONS

# Boundary conditions so far only include restricted degrees. They are defined
# by the restricted nodes number, and the value 1 for all restricted nodal 
# directions and the value 0 for all free nodal directions.
#                        [NodeNr,    x,    y,   rz]
rotated_degrees = [[0, -np.pi/4]]

restricted_degrees = [[0, 0, 1, 0]]

springs = [[0, 10, 10, 10]]
boundary_conditions = {'Rotated Degrees': rotated_degrees,'Restricted Degrees': restricted_degrees, 'Springs': springs}

# MODEL

# All the information on the model is stored in one dictionary.
model = {'Nodes': nodes, 'Beams': beams, 'Loads': loads,
         'Boundary Conditions': boundary_conditions}

# STRUCTURE ANALYSIS

# The verification and the calculation of the model are carried out by the main
# function of the structureanalysis package. It returns the displacements and
# the internal forces in a list with a dictionary for each loadgroup. The 
# values are aranged beamwise. Also it returns the restricted degrees reaction
# in the same format as they were defined.

displacements, internal_forces, rd_reactions, spring_reactions = structure_analysis(model)

# Print the support reactions.
for i in range(len(rd_reactions)):
    print(rd_reactions[i], '\n')
    print(spring_reactions[i], '\n', '\n')
