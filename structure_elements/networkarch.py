import numpy as np

from structure_analysis import structure_analysis
from structure_elements.element import connect_inner_lists, multiply_effect, add_effects


class NetworkArch:
    def __init__(self, arch, tie, hangers, nodes):
        self.arch = arch
        self.tie = tie
        self.hangers = hangers
        self.nodes = nodes
        return

    def get_beams(self):
        tie_nodes, tie_stiffness = self.tie.get_beams()
        arch_nodes, arch_stiffness = self.arch.get_beams()

        # first hanger index is needed to specify the releases
        i_1 = len(self.tie) + len(self.arch)
        hanger_nodes, hanger_stiffness, hanger_releases = self.hangers.get_beams(i_1)

        beams_nodes = tie_nodes + arch_nodes + hanger_nodes
        beams_stiffness = tie_stiffness + arch_stiffness + hanger_stiffness
        beams = {'Nodes': beams_nodes, 'Stiffness': beams_stiffness, 'Releases': hanger_releases}
        return beams

    def create_model(self):
        structural_nodes = self.nodes.structural_nodes()
        beams = self.get_beams()
        loads = []
        restricted_degrees = [[self.tie.nodes[0].index, 1, 1, 0, 0], [self.tie.nodes[-1].index, 0, 1, 0, 0]]
        boundary_conditions = {'Restricted Degrees': restricted_degrees}
        model = {'Nodes': structural_nodes, 'Beams': beams, 'Loads': loads,
                 'Boundary Conditions': boundary_conditions}
        return model

    def internal_forces_to_effects(self, internal_forces):
        i_tie = len(self.tie)
        i_arch = i_tie + len(self.arch)
        effects = {}
        for key in internal_forces:
            effects[key] = np.array(connect_inner_lists(internal_forces[key][:i_arch]))

        effects_hangers = np.array([eff[0] for eff in internal_forces['Normal Force'][i_arch:]])
        effects['Normal Force'] = np.hstack((effects['Normal Force'], effects_hangers))
        return effects

    def set_effects(self, effects, name):
        if type(effects) is str:
            effects = self.get_effects(effects)

        i_tie = self.tie.effect_length()
        i_arch = i_tie + self.arch.effect_length()
        for key in effects:
            self.tie.set_effects(effects[key][:i_tie], name, key=key)
            self.arch.set_effects(effects[key][i_tie:i_arch], name, key=key)
        if 'D/C_1' not in effects:
            self.tie.calculate_doc(name)
            self.arch.calculate_doc(name)

        effects_hangers = {'Normal Force': effects['Normal Force'][i_arch:]}
        self.hangers.set_effects(effects_hangers, name)
        return

    def get_effects(self, name, key=''):
        effects = self.tie.get_effects(name)
        arch_effects = self.arch.get_effects(name)
        hanger_effects = self.hangers.get_effects(name)

        for arch_key in arch_effects:
            effects[arch_key] = np.hstack((effects[arch_key], arch_effects[arch_key]))
        effects['Normal Force'] = np.hstack((effects['Normal Force'], hanger_effects['Normal Force']))
        if key:
            return effects[key]
        else:
            return effects

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

    def calculate_load_cases(self, q_d, q_c, qc_fatigue):
        model = self.create_model()

        n_tie = len(self.tie)
        loads_tie = self.tie.self_weight()
        loads_arch = self.arch.self_weight(first_index=n_tie)
        loads_dc = [{'Distributed': loads_tie['Distributed'] + loads_arch['Distributed'], 'Nodal':loads_tie['Nodal']}]
        model['Loads'] = loads_dc
        for node in self.tie.cross_girders_nodes:
            model['Loads'].append({'Nodal': [[node.index, 0, -1, 0]]})

        d, i_f, rd, sp = structure_analysis(model)
        effects = self.internal_forces_to_effects(i_f[0])
        self.set_effects(effects, 'DC')

        added = '0'
        inclusive = '0'
        exclusive = '0'
        for i in range(len(self.tie.cross_girders_nodes)):
            name = 'F'+str(i+1)
            effects = self.internal_forces_to_effects(i_f[i+1])
            self.set_effects(effects, name)
            added += ' + ' + name
            inclusive += ', 0/' + name
            exclusive += '/' + name

        self.set_effects(added, 'Added')
        self.set_range(inclusive, 'Inclusive')
        self.set_range(exclusive, 'Exclusive')

        span = self.tie.span
        n = self.tie.cross_girders_amount
        f_d = span * q_d / (n+1)
        f_c = q_c
        g_c = self.tie.force_utilities

        self.set_effects(str(g_c)+' Added', 'DW')
        self.set_range(str(f_d)+' Inclusive', 'LLd')
        self.set_range(str(f_c)+' Exclusive', 'LLc')
        self.set_range(str(qc_fatigue)+' Exclusive', 'Fatigue')

        self.set_effects('DC + DW', 'DL')
        self.set_effects('Permanent - DL', 'EL')
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

        forces = []
        for hanger in self.hangers:
            force = hanger.cross_section.wind_effects.get('Normal Force', [0])
            forces.append([force[0], force[-1]])
        effects = {'Normal Force': np.array(forces).transpose()}
        self.hangers.set_effects(effects, 'WS')
        return

    def calculate_ultimate_limit_states(self):
        self.set_range('EL, 1.25 DC/0.9 DC, 1.5 DW/0.65 DW, 0/1.75 LL', 'Strength-I')
        self.add_key('Strength-I', 'Moment y', 0)

        self.set_range('EL, 1.25 DC/0.9 DC, 1.5 DW/0.65 DW', 'Strength-III_temp')
        self.add_key('Strength-III_temp', 'Moment y', 0)
        self.set_range('Strength-III_temp, 1.4 WS', 'Strength-III')

        self.set_range('EL, 1.5 DC, 1.5 DW', 'Strength-IV')
        self.add_key('Strength-IV', 'Moment y', 0)

        self.assign_range_to_sections(['Strength-I', 'Strength-III', 'Strength-IV'])
        self.hangers.assign_range_to_sections('Fatigue')
        return

    def calculate_tie_fracture(self, q_d, q_c):

        self.tie.calculate_fracture_stress('0')
        self.tie.calculate_fracture_stress('EL')
        self.tie.calculate_fracture_stress('DC')
        self.tie.calculate_fracture_stress('DW')

        inclusive = '0'
        exclusive = '0'
        for i in range(len(self.tie.cross_girders_nodes)):
            name = 'F'+str(i+1)
            self.tie.calculate_fracture_stress(name)
            inclusive += ', 0/' + name
            exclusive += '/' + name

        self.set_range(inclusive, 'Inclusive')
        self.set_range(exclusive, 'Exclusive')

        span = self.tie.span
        n = self.tie.cross_girders_amount
        f_d = span * q_d / (n+1)
        f_c = q_c

        self.set_range(str(f_d) + ' Inclusive', 'LLd')
        self.set_range(str(f_c) + ' Exclusive', 'LLc')

        self.set_range('LLc, LLd', 'LL')

        self.set_range('EL, 1.25 DC, 1.5 DW, 1.3 LL', 'Tie Fracture')
        self.tie.assign_range_to_sections('Tie Fracture')
        return

    # def calculate_cable_loss(self, name, i_hanger, q_d, q_c, ll_factor, daf=1):
    #     hanger = self.hangers[i_hanger]
    #     span = self.tie.span
    #     n = self.tie.cross_girders_amount
    #     f_d = span * q_d / (n + 1)
    #
    #     # Find worst load arrangement
    #     self.set_range('EL + 1.2 DC + 1.4 DW', 'Cable loss')
    #     load = '0'
    #     max_hanger_force = 0
    #     max_hanger_force_i = 0
    #     for i in range(len(self.tie.cross_girders_nodes)):
    #         hanger_force = hanger.effects_N['F'+str(i+1)]
    #         if hanger_force > 0:
    #             load += ' + ' + str(f_d) + ' F'+str(i+1)
    #         if hanger_force > max_hanger_force:
    #             max_hanger_force = hanger_force
    #             max_hanger_force_i = i
    #     load += ' + ' + str(q_c) + ' F'+str(max_hanger_force_i+1)
    #     effects = self.get_effects(load)
    #     self.set_effects(effects, 'LL_'+name)
    #     effects = self.get_effects('EL + 1.2 DC + 1.4 DW + '+str(ll_factor)+' LL_'+name)
    #     self.set_effects(effects, name+'_static')
    #     hanger_force = hanger.effects_N[name+'_static']
    #
    #     model = self.create_model()
    #     i_tie = len(self.tie)
    #     i_arch = i_tie + len(self.arch)
    #     i = i_arch + i_hanger
    #     model['Beams']['Nodes'].pop(i)
    #     model['Beams']['Stiffness'].pop(i)
    #     model['Beams']['Releases'] = model['Beams']['Releases'][:-1]
    #
    #     vertical_force = hanger_force * np.sin(hanger.inclination)
    #     horizontal_force = hanger_force * np.cos(hanger.inclination)
    #     loads_nodal = [[hanger.tie_node.index, -horizontal_force, -vertical_force, 0],
    #                    [hanger.arch_node.index, horizontal_force, vertical_force, 0]]
    #     model['Loads'] = [{'Nodal': loads_nodal}]
    #     # plot_loads_old(model, 0, 'Test')
    #     # pyplot.show()
    #
    #     d, i_f, rd, sp = structure_analysis(model)
    #     i_f[0]['Normal Force'].insert(i, [-hanger_force/daf])
    #     effects = self.internal_forces_to_effects(i_f[0])
    #     self.set_effects(effects, name+'_dyn')
    #     self.set_effects(name + '_static + ' + str(daf) + ' ' + name + '_dyn', name)
    #     self.assign_range_to_sections([name])
    #     # self.hangers.effects[0, i_hanger] = 0
    #     # hanger.effects_N[name][0] = 0
    #     return

    def calculate_cable_loss(self, events):
        model = self.create_model()
        n = self.tie.effect_length() + self.arch.effect_length()

        for hanger in self.hangers.hanger_sets[0]:
            vertical_force = np.sin(hanger.inclination)
            horizontal_force = np.cos(hanger.inclination)
            loads_nodal = [[hanger.tie_node.index, -horizontal_force, -vertical_force, 0],
                           [hanger.arch_node.index, horizontal_force, vertical_force, 0]]
            model['Loads'].append({'Nodal': loads_nodal})

        d, i_f, rd, sp = structure_analysis(model)
        for i, hanger in enumerate(self.hangers.hanger_sets[0]):
            effects_i = self.internal_forces_to_effects(i_f[i])
            hanger_force = effects_i['Normal Force'][n+i]
            effects_i['Normal Force'][n + i] = 0
            factor = 1/(1-hanger_force)
            effects_i = multiply_effect(effects_i, factor)
            self.set_effects(effects_i, 'L'+str(i+1))

        n_girders = self.tie.cross_girders_amount
        span = self.tie.span
        for event in events:
            name = event['Name']
            q_d = event['Distributed Load']
            q_c = event['Concentrated Load']
            c_ll = event['Factor LL']
            daf = event['Dynamic Amplification Factor']
            f_d = span * q_d / (n_girders + 1)
            range_name = ''
            for i, hanger in enumerate(self.hangers.hanger_sets[0]):
                load = '0'
                max_hanger_force = 0
                max_hanger_force_i = 0
                for i_girder in range(len(self.tie.cross_girders_nodes)):
                    hanger_force = hanger.effects_N['F' + str(i_girder + 1)]
                    if hanger_force > 0:
                        load += ' + ' + str(c_ll * f_d) + ' F' + str(i_girder + 1)
                    if hanger_force > max_hanger_force:
                        max_hanger_force = hanger_force
                        max_hanger_force_i = i_girder
                load += ' + ' + str(c_ll * q_c) + ' F' + str(max_hanger_force_i + 1)
                effects_0 = self.get_effects('EL + 1.2 DC + 1.4 DW + '+load)

                hanger_force = effects_0['Normal Force'][n+i]
                effects_i = self.get_effects(str(daf * hanger_force)+' L'+str(i+1))
                effects = add_effects(effects_0, effects_i)
                effects['Normal Force'][n+i] = 0
                self.set_effects(effects, name+'_'+str(i+1))
                range_name += name+'_'+str(i+1)+'/'
            self.set_range(range_name[:-1], name)
            self.assign_range_to_sections([name])
        return
