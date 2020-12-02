import numpy as np

from plotting.model import plot_model
from plotting.save import save_plot
from structure_analysis import structure_analysis


def define_by_peak_moment(arch, nodes, hangers, mz_0, peak_moment=0):
    arch.assign_permanent_effects(nodes, hangers, 0, -mz_0)
    moments_arch = arch.effects['Permanent']['Moment']
    moment_max = max(moments_arch)
    n_0 = (moment_max - peak_moment) / arch.rise
    return n_0


def zero_displacement(tie, nodes, hangers, dof_rz=True, plot=False):
    structural_nodes = nodes.structural_nodes()
    beams_nodes, beams_stiffness = tie.get_beams()
    beams = {'Nodes': beams_nodes, 'Stiffness': beams_stiffness}
    load_group = tie.permanent_loads()

    restricted_degrees = [[tie.nodes[0].index, 1, 1, int(dof_rz), 0]]
    restricted_degrees += [[tie.nodes[-1].index, 1, 1, int(dof_rz), 0]]
    for hanger in hangers:
        restricted_degrees += [[hanger.tie_node.index, 0, 1, 0, 0]]

    boundary_conditions = {'Restricted Degrees': restricted_degrees}
    model = {'Nodes': structural_nodes, 'Beams': beams, 'Loads': [load_group],
             'Boundary Conditions': boundary_conditions}

    d_tie, if_tie, rd_tie, sp_tie = structure_analysis(model)
    mz_0 = if_tie[0]['Moment'][0][0] if dof_rz else 0

    # Assign the support reaction forces to the hangers
    nodes_x = [model['Nodes']['Location'][rd[0]][0] for rd in rd_tie[0][2:]]
    nodes_forces = [rd[2] for rd in rd_tie[0][2:]]
    # Assign the reaction forces to the hangers
    sine_proportional(nodes_x, nodes_forces, hangers)
    # sine_length_proportional(nodes_x, nodes_forces, hangers)

    if plot:
        # Adapt loads to have a nice plot
        load_distributed = load_group['Distributed'][0]
        load_distributed[2] = tie.span
        load_group = {'Distributed': [load_distributed]}
        loads = [load_group]
        model = {'Nodes': structural_nodes, 'Beams': beams, 'Loads': loads,
                 'Boundary Conditions': boundary_conditions}

        fig, ax = plot_model(model, tie)
        save_plot(fig, 'Models', 'Hanger Forces')
    return mz_0


def sine_proportional(nodes_x, nodes_forces, hangers):
    for i in range(len(nodes_forces)):
        sine_sum = 0
        for hanger in hangers:
            if hanger.tie_node.x == nodes_x[i]:
                sine_sum += np.sin(hanger.inclination)
        hanger_force = nodes_forces[i] / sine_sum
        for hanger in hangers:
            if hanger.tie_node.x == nodes_x[i]:
                hanger.prestressing_force = hanger_force
    return


def sine_length_proportional(nodes_x, nodes_forces, hangers):
    for i in range(len(nodes_forces)):
        sine_length_sum = 0
        for hanger in hangers:
            if hanger.tie_node.x == nodes_x[i]:
                sine_length_sum += np.sin(hanger.inclination) ** 2 * hanger.length()
        hanger_force = nodes_forces[i] / sine_length_sum
        for hanger in hangers:
            if hanger.tie_node.x == nodes_x[i]:
                hanger.prestressing_force = hanger_force * np.sin(hanger.inclination) * hanger.length()
    return
