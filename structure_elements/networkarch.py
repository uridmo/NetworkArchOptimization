from matplotlib import pyplot
from numpy import linspace

from plotting.model import plot_model
from plotting.save import save_plot
from structure_analysis import structure_analysis


class NetworkArch:
    def __init__(self, arch, tie, hangers):
        self.arch = arch
        self.tie = tie
        self.hangers = hangers
        self.support_reaction = {}
        return

    def get_beams(self):
        tie_nodes, tie_stiffness = self.tie.get_beams()
        arch_nodes, arch_stiffness = self.arch.get_beams()

        # Indices for hangers are needed to specify the releases
        i_1 = len(self.tie) + len(self.arch)
        i_2 = i_1 + len(self.hangers)
        hanger_nodes, hanger_stiffness, hanger_releases = self.hangers.get_beams(range(i_1, i_2))

        beams_nodes = tie_nodes + arch_nodes + hanger_nodes
        beams_stiffness = tie_stiffness + arch_stiffness + hanger_stiffness
        beams = {'Nodes': beams_nodes, 'Stiffness': beams_stiffness, 'Releases': hanger_releases}
        return beams

    def create_model(self, nodes, plot=False):
        structural_nodes = nodes.structural_nodes()
        beams = self.get_beams()
        loads = []
        restricted_degrees = [[self.tie.nodes[0].index, 1, 1, 0, 0], [self.tie.nodes[-1].index, 0, 1, 0, 0]]
        boundary_conditions = {'Restricted Degrees': restricted_degrees}
        model = {'Nodes': structural_nodes, 'Beams': beams, 'Loads': loads,
                 'Boundary Conditions': boundary_conditions}

        if plot:
            fig, ax = plot_model(model, self)
            save_plot(fig, 'Models', 'Network Arch Bridge')
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
        self.tie.get_range(range_name, name=name)
        self.arch.get_range(range_name, name=name)
        self.hangers.get_range(range_name, name=name)
        return

    def assign_range_to_sections(self):
        self.tie.assign_range_to_sections()
        self.arch.assign_range_to_sections()
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

        d, i_f, rd = structure_analysis(model)
        self.support_reaction['Permanent'] = rd[0]
        self.set_effects(i_f[0], 'DL')
        return

    def calculate_distributed_live_load(self, nodes, q, n_loads):
        span = self.tie.nodes[-1].x
        model = self.create_model(nodes)
        x_tie = linspace(0, span, num=n_loads+1)

        for i in range(n_loads):
            model['Loads'].append(self.tie.distributed_live_load(q, x_tie[i], x_tie[i+1]))

        d, i_f, rd = structure_analysis(model)

        range_name = ''
        for i in range(n_loads):
            name = 'LL'+str(i+1)
            self.set_effects(i_f[i], name)
            self.support_reaction[name] = rd[i]
            range_name += '0/' + name + ', '
        range_name = range_name[0:-2]
        self.set_range(range_name, 'LL')
        return

    def plot_elements(self, ax):
        self.tie.plot_elements(ax)
        self.arch.plot_elements(ax)
        self.hangers.plot_elements(ax)
        return

    def plot_effects(self, name, key, fig=None, fig_size=(4, 4), color='black'):
        if not fig:
            fig = pyplot.figure(figsize=fig_size, dpi=240)
        ax = fig.add_subplot(211)
        ax.set_title('Arch')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        self.arch.plot_effects(ax, name, key, color=color)
        ax.set_xlim([0, self.tie.nodes[-1].x])

        ax = fig.add_subplot(212)
        ax.set_title('Tie')
        self.tie.plot_effects(ax, name, key, color=color)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_xlim([0, self.tie.nodes[-1].x])

        pyplot.show()
        return
