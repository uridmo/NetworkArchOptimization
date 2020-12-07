from structure_analysis import structure_analysis


class NetworkArch:
    def __init__(self, arch, tie, hangers):
        self.arch = arch
        self.tie = tie
        self.hangers = hangers
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
            self.tie.calculate_doc(name)
            self.arch.set_effects(effects[key][i_tie:i_arch], name, key=key)
            self.arch.calculate_doc(name)
        self.hangers.set_effects(effects['Normal Force'][i_arch:], name)
        return

    def set_range(self, range_name, name):
        self.tie.get_range(range_name, name=name)
        self.arch.get_range(range_name, name=name)
        self.hangers.get_range(range_name, name=name)
        return

    def assign_range_to_sections(self, names):
        for name in names:
            self.tie.assign_range_to_sections(name)
            self.arch.assign_range_to_sections(name)
            self.hangers.assign_range_to_sections(name)
        return

    def add_key(self, name, key, value):
        self.tie.add_key(name, key, value)
        self.arch.add_key(name, key, value)
        return

    def calculate_load_cases(self, nodes, q_d, q_c):
        model = self.create_model(nodes)

        n_tie = len(self.tie)
        loads_tie = self.tie.self_weight()
        loads_arch = self.arch.self_weight(first_index=n_tie)
        loads_dc = [{'Distributed': loads_tie['Distributed'] + loads_arch['Distributed'], 'Nodal':loads_tie['Nodal']}]
        model['Loads'] = loads_dc
        for node in self.tie.cross_girders_nodes:
            model['Loads'].append({'Nodal': [[node.index, 0, -1, 0]]})

        d, i_f, rd, sp = structure_analysis(model)
        self.set_effects(i_f[0], 'DC')

        added = '0'
        inclusive = '0'
        exclusive = '0'
        for i in range(len(self.tie.cross_girders_nodes)):
            name = 'F'+str(i+1)
            self.set_effects(i_f[i+1], name)
            added += ' + ' + name
            inclusive += ', 0/' + name
            exclusive += '/' + name

        self.set_range(added, 'Added')
        self.set_range(inclusive, 'Inclusive')
        self.set_range(exclusive, 'Exclusive')

        span = self.tie.span
        n = self.tie.cross_girders_amount
        f_d = span * q_d / (n+1)
        f_c = q_c
        g_c = self.tie.utilities

        self.set_range(str(g_c)+' Added', 'DW')
        self.set_range(str(f_d)+' Inclusive', 'LLd')
        self.set_range(str(f_c)+' Exclusive', 'LLc')

        self.set_range('DC + DW', 'DL')
        self.set_range('Permanent - DL', 'EL')
        self.set_range('LLc, LLd', 'LL')
        return

    def assign_wind_effects(self):
        self.set_range('0', 'WS')
        for element in [self.arch, self.tie]:
            element.add_key('WS', 'Moment y', 0)
            cs_i = element.get_cross_sections()
            for cs in set(element.cross_sections):
                mask = cs_i == cs
                for effect in cs.wind_effects:
                    element.effects['WS'][effect][0, mask] = cs.wind_effects[effect][0]
                    element.effects['WS'][effect][1, mask] = cs.wind_effects[effect][-1]

        # Get the first hanger
        hanger = self.hangers.hanger_sets[0].hangers[0]
        cs = hanger.cross_section
        for name in cs.wind_effects:
            effect = cs.wind_effects[name]
            self.hangers.set_effects(effect, 'WS')
        return

    def calculate_ultimate_limit_states(self):
        self.set_range('EL, 1.25 DC/0.9 DC, 1.5 DW/0.65 DW, 0/1.75 LL', 'Strength-I')
        self.add_key('Strength-I', 'Moment y', 0)

        self.set_range('EL, 1.25 DC/0.9 DC, 1.5 DW/0.65 DW', 'Strength-III')
        self.add_key('Strength-III', 'Moment y', 0)
        self.set_range('Strength-III, 1.4 WS', 'Strength-III')

        self.set_range('EL, 1.5 DC, 1.5 DW', 'Strength-IV')
        self.add_key('Strength-IV', 'Moment y', 0)

        self.assign_range_to_sections(['Strength-I', 'Strength-III', 'Strength-IV'])

        return
