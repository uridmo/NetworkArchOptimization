from structure_analysis import structure_analysis
from structure_analysis.plotting import plot_loads


class NetworkArch:
    def __init__(self, arch, tie, hangers):
        self.arch = arch
        self.tie = tie
        self.hangers = hangers
        self.support_reaction = {}
        return

    def get_beams(self):
        tie_nodes, tie_stiffness = self.tie.beams()
        arch_nodes, arch_stiffness = self.arch.beams()

        i_1 = len(self.tie) + len(self.arch)
        i_2 = i_1 + len(self.hangers)
        hanger_nodes, hanger_stiffness, hanger_releases = self.hangers.get_beams(range(i_1, i_2))

        beams_nodes = tie_nodes + arch_nodes + hanger_nodes
        beams_stiffness = tie_stiffness + arch_stiffness + hanger_stiffness
        beams = {'Nodes': beams_nodes, 'Stiffness': beams_stiffness, 'Releases': hanger_releases}
        return beams

    def create_model(self, nodes, plot=False):
        # Define the list of all nodes
        structural_nodes = nodes.structural_nodes()

        # Define the beams
        beams = self.get_beams()

        # Create an empty load group
        loads = [{}]

        # Define the boundary conditions
        restricted_degrees = [[self.tie.nodes[0].index, 1, 1, 0, 0], [self.tie.nodes[-1].index, 0, 1, 0, 0]]
        boundary_conditions = {'Restricted Degrees': restricted_degrees}

        model = {'Nodes': structural_nodes, 'Beams': beams, 'Loads': loads,
                 'Boundary Conditions': boundary_conditions}

        if plot:
            plot_loads(model, 0, 'Network arch structure')
        return model

    def assign_effects(self, d, i_f, rd, name):
        i_tie = len(self.tie)
        i_arch = i_tie + len(self.arch)

        if name not in self.arch.impacts:
            self.arch.impacts[name] = {}
        if name not in self.tie.impacts:
            self.tie.impacts[name] = {}

        for effect in ['Moment', 'Shear Force', 'Normal Force']:
            self.arch.impacts[name][effect] = i_f[effect][:i_tie]
            self.tie.impacts[name][effect] = i_f[effect][i_tie:i_arch]

        self.tie.impacts[name]['Normal Force'] = i_f['Normal Force'][i_arch:]

        self.support_reaction[name] = rd
        return

    def dead_load(self, nodes, plot=False):
        n_tie = len(self.tie)
        n_arch = len(self.arch)

        model = self.create_model(nodes, plot=plot)

        loads_tie = self.tie.self_weight()
        loads_arch = self.arch.self_weight(range(n_tie, n_arch))
        loads = [{'Distributed': loads_tie + loads_arch}]
        model['Loads'] = loads

        d, i_f, rd = structure_analysis(model, discType='Lengthwise', discLength=1)
        self.support_reaction['Permanent'] = rd[0]
        self.assign_effects(d[0], i_f[0], rd[0], 'Self Weight')

        return
