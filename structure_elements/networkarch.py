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

    def calculate_dead_load(self, nodes):
        n_tie = len(self.tie)
        model = self.create_model(nodes)
        loads_tie = self.tie.self_weight()
        loads_arch = self.arch.self_weight(first_index=n_tie)
        loads_dc = [{'Distributed': loads_tie['Distributed'] + loads_arch['Distributed'], 'Nodal': loads_tie['Nodal']}]
        loads_dw = self.tie.load_group_utilities()
        model['Loads'] = [loads_dc] + [loads_dw]

        d, i_f, rd, sp = structure_analysis(model)
        self.set_effects(i_f[0], 'DC')
        self.set_effects(i_f[1], 'DW')
        self.set_range('Permanent + -1 DC + -1 DW', 'EL')
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

        d, i_f, rd, sp = structure_analysis(model)

        # Save distributed effects and calculate inclusive range
        range_name = ''
        for i in range(n+2):
            name = 'LLd'+str(i+1)
            self.set_effects(i_f[i], name)
            range_name += '0/' + name + ', '
        range_name = range_name[0:-2]
        self.set_range(range_name, 'LLd')

        # Save concentrated effects and calculate exclusive range
        range_name = '0/'
        for i in range(n+2):
            name = 'LLc'+str(i+1)
            self.set_effects(i_f[n+2+i], name)
            range_name += name + '/'
        range_name = range_name[0:-1]
        self.set_range(range_name, 'LLc')

        # Merge the two ranges
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
