import numpy as np

from plotting.model import plot_model
from plotting.save import save_plot
from structure_analysis import structure_analysis
from structure_analysis import verify_input


def zero_displacement(tie, nodes, hangers, dof_rz=False, plot=False):
    structural_nodes = nodes.structural_nodes()
    beams_nodes, beams_stiffness = tie.get_beams()
    beams = {'Nodes': beams_nodes, 'Stiffness': beams_stiffness}
    load_distributed = tie.self_weight()
    loads = [{'Distributed': load_distributed}]

    restricted_degrees = [[tie.nodes[0].index, 1, 1, int(dof_rz), 0]]
    restricted_degrees += [[tie.nodes[-1].index, 1, 1, int(dof_rz), 0]]
    for hanger in hangers:
        restricted_degrees += [[hanger.tie_node.index, 0, 1, 0, 0]]

    boundary_conditions = {'Restricted Degrees': restricted_degrees}
    model = {'Nodes': structural_nodes, 'Beams': beams, 'Loads': loads,
             'Boundary Conditions': boundary_conditions}

    verify_input(model)
    d_tie, if_tie, rd_tie = structure_analysis(model)
    mz_0 = if_tie[0]['Moment'][0][0] if dof_rz else 0

    # Assign the support reaction forces to the hangers
    nodes_x = [model['Nodes']['Location'][rd[0]][0] for rd in rd_tie[0][2:]]
    nodes_forces = [rd[2] for rd in rd_tie[0][2:]]
    nodes_forces2hanger_forces_equal(nodes_x, nodes_forces, hangers)

    if plot:
        # Adapt loads to have a nice plot
        load_distributed = load_distributed[0]
        load_distributed[2] = tie.end_node.x
        load_group = {'Distributed': [load_distributed]}
        loads = [load_group]
        model = {'Nodes': structural_nodes, 'Beams': beams, 'Loads': loads,
                 'Boundary Conditions': boundary_conditions}

        fig, ax = plot_model(model, tie)
        save_plot(fig, 'Models', 'Hanger Forces')
    return mz_0


def nodes_forces2hanger_forces_equal(nodes_x, nodes_forces, hangers):
    for i in range(len(nodes_forces)):
        sinus_sum = 0
        for hanger in hangers:
            if hanger.tie_node.x == nodes_x[i]:
                sinus_sum += np.sin(hanger.inclination)
        hanger_force = nodes_forces[i] / sinus_sum
        for hanger in hangers:
            if hanger.tie_node.x == nodes_x[i]:
                hanger.prestressing_force = hanger_force
    return
