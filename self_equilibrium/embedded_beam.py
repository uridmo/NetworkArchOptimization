import numpy as np

from structure_analysis import structure_analysis


def embedded_beam(tie, nodes, hangers, stiffness):
    structural_nodes = nodes.structural_nodes()
    beams_nodes, beams_stiffness = tie.get_beams()
    beams = {'Nodes': beams_nodes, 'Stiffness': beams_stiffness}
    load_group = tie.self_weight()

    restricted_degrees = [[tie.nodes[0].index, 1, 0, 0], [tie.nodes[-1].index, 0, 0, 0]]
    # restricted_degrees = []
    springs = []
    for hanger in hangers:
        angle = hanger.inclination
        c, s = np.cos(angle), np.sin(angle)
        springs += [[hanger.tie_node.index, 0, stiffness*s, 0]]
    springs.append([tie.nodes[0].index, stiffness, 0, stiffness*1000])
    springs.append([tie.nodes[-1].index, 1, 0, stiffness*1000])

    boundary_conditions = {'Springs': springs, 'Restricted Degrees': restricted_degrees}
    model = {'Nodes': structural_nodes, 'Beams': beams, 'Loads': [load_group],
             'Boundary Conditions': boundary_conditions}

    d_tie, if_tie, rd_tie, sp_tie = structure_analysis(model)
    mz_0 = 0  # if_tie[0]['Moment'][0][0] if dof_rz else 0

    # Assign the support reaction forces to the hangers
    forces = []
    for sp, hanger in zip(sp_tie[0], hangers):
        forces.append(sp[2]/np.sin(hanger.inclination))
    hangers.set_prestressing_forces(forces)
    return mz_0
