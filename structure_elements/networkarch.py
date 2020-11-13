from matplotlib import pyplot

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

        # Indices for hangers are needed to specify the releases
        i_1 = len(self.tie) + len(self.arch)
        i_2 = i_1 + len(self.hangers)
        hanger_nodes, hanger_stiffness, hanger_releases = self.hangers.beams(range(i_1, i_2))

        beams_nodes = tie_nodes + arch_nodes + hanger_nodes
        beams_stiffness = tie_stiffness + arch_stiffness + hanger_stiffness
        beams = {'Nodes': beams_nodes, 'Stiffness': beams_stiffness, 'Releases': hanger_releases}
        return beams

    def create_model(self, nodes, plot=False):
        structural_nodes = nodes.structural_nodes()
        beams = self.get_beams()
        loads = [{}]
        restricted_degrees = [[self.tie.nodes[0].index, 1, 1, 0, 0], [self.tie.nodes[-1].index, 0, 1, 0, 0]]
        boundary_conditions = {'Restricted Degrees': restricted_degrees}
        model = {'Nodes': structural_nodes, 'Beams': beams, 'Loads': loads,
                 'Boundary Conditions': boundary_conditions}

        if plot:
            ax = plot_loads(model, 0, 'Network arch structure')
            self.arch.plot_effects(ax, nodes, 'Test 1', 'Moment')
            pyplot.show()
        return model

    def set_effects(self, effects, name):
        i_tie = len(self.tie)
        i_arch = i_tie + len(self.arch)
        for key in effects:
            self.tie.set_effects(effects[key][:i_tie], name, key=key)
            self.arch.set_effects(effects[key][i_tie:i_arch], name, key=key)
            self.hangers.set_effects(effects[key][i_arch:], name, key=key)
        return

    def set_range(self, range_name, name):
        self.tie.set_range(range_name, name=name)
        self.arch.set_range(range_name, name=name)
        self.hangers.set_range(range_name, name=name)
        return

    def assign_support_reaction(self, rd, name):
        self.support_reaction[name] = rd
        return

    def calculate_dead_load(self, nodes, plot=False):
        n_tie = len(self.tie)
        n_arch = len(self.arch)

        model = self.create_model(nodes, plot=plot)

        loads_tie = self.tie.self_weight()
        loads_arch = self.arch.self_weight(range(n_tie, n_arch))
        loads = [{'Distributed': loads_tie + loads_arch}]
        model['Loads'] = loads

        d, i_f, rd = structure_analysis(model, discType='Lengthwise', discLength=1)
        self.support_reaction['Permanent'] = rd[0]
        self.set_effects(i_f[0], 'DL')

        return
