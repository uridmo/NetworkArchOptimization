from matplotlib import pyplot

from plotting.adjustments import adjust_plot
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

    def create_model(self, nodes):
        structural_nodes = nodes.structural_nodes()
        beams = self.get_beams()
        loads = []
        restricted_degrees = [[self.tie.nodes[0].index, 1, 1, 0, 0], [self.tie.nodes[-1].index, 0, 1, 0, 0]]
        boundary_conditions = {'Restricted Degrees': restricted_degrees}
        model = {'Nodes': structural_nodes, 'Beams': beams, 'Loads': loads,
                 'Boundary Conditions': boundary_conditions}
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
        self.tie.assign_range_to_regions()
        self.arch.assign_range_to_regions()
        return

    def assign_support_reaction(self, rd, name):
        self.support_reaction[name] = rd
        return

    def calculate_dead_load(self, nodes):
        n_tie = len(self.tie)
        model = self.create_model(nodes)
        loads_tie = self.tie.self_weight()
        loads_arch = self.arch.self_weight(first_index=n_tie)
        loads = [{'Distributed': loads_tie['Distributed'] + loads_arch['Distributed'], 'Nodal': loads_tie['Nodal']}]
        model['Loads'] = loads

        d, i_f, rd = structure_analysis(model)
        self.support_reaction['Permanent'] = rd[0]
        self.set_effects(i_f[0], 'DL')
        return

    def calculate_live_load(self, nodes, q_d, q_c):
        span = self.tie.span
        n = self.tie.cross_girders_amount
        f_d = -span * q_d / (n+1)
        f_c = -q_c

        # Define the model
        model = self.create_model(nodes)
        loads = model['Loads']
        for f in [f_d, f_c]:
            loads.append({'Nodal': [[self.tie.nodes[0].index, 0, f / 2, 0]]})
            for i in range(n):
                loads.append({'Nodal': [[self.tie.cross_girders_nodes[i].index, 0, f, 0]]})
            loads.append({'Nodal': [[self.tie.nodes[-1].index, 0, f / 2, 0]]})

        d, i_f, rd = structure_analysis(model)

        # Save distributed effects and calculate inclusive range
        range_name = ''
        for i in range(n+2):
            name = 'LLd'+str(i+1)
            self.set_effects(i_f[i], name)
            self.support_reaction[name] = rd[i]
            range_name += '0/' + name + ', '
        range_name = range_name[0:-2]
        self.set_range(range_name, 'LLd')

        # Save concentrated effects and calculate exclusive range
        range_name = '0/'
        for i in range(n+2):
            name = 'LLc'+str(i+1)
            self.set_effects(i_f[n+i], name)
            self.support_reaction[name] = rd[n+i]
            range_name += name + '/'
        range_name = range_name[0:-1]
        self.set_range(range_name, 'LLc')

        # Merge the two ranges
        self.set_range('LLc, LLd', 'LL')
        return

    def plot_elements(self, ax):
        self.tie.plot_elements(ax)
        self.arch.plot_elements(ax)
        self.hangers.plot_elements(ax)
        return

    def plot_effects(self, name, key, fig=None, color='black'):
        if not fig:
            fig, axs = pyplot.subplots(3, 1, figsize=(4, 6), dpi=240)
        else:
            axs = fig.get_axes()

        self.arch.plot_effects(axs[0], name, key, color=color)
        self.tie.plot_effects(axs[1], name, key, color=color)
        self.hangers.plot_effects(axs[2], name, color=color)
        return fig
