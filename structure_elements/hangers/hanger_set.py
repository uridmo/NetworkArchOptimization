from copy import deepcopy
import numpy as np

from structure_elements.hangers.hanger import Hanger


class HangerSet:
    def __init__(self):
        self.hangers = []
        return

    def __repr__(self):
        return repr(self.hangers)

    def __len__(self):
        return len(self.hangers)

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if self.i < len(self):
            result = self.hangers[self.i]
            self.i += 1
            return result
        else:
            raise StopIteration

    def add_hanger(self, nodes, x_tie, angle):
        node = nodes.add_node(x_tie, 0)
        hanger = Hanger(node, angle)
        self.hangers.append(hanger)
        return

    def mirror(self, nodes, span):
        hanger_set_mirrored = deepcopy(self)
        for hanger in hanger_set_mirrored:
            hanger.tie_node = nodes.add_node(span - hanger.tie_node.x, 0)
            hanger.inclination = np.pi - hanger.inclination
        hanger_set_mirrored.hangers.sort(key=lambda h: h.tie_node.x)
        hangers = [self, hanger_set_mirrored]
        return hangers

    def plot_effects(self, ax, name, key='', label='', c='black', lw=1.0, ls='-'):
        x = []
        n = []
        if not key:
            if type(self.hangers[0].effects_N[name]) is not dict:
                for hanger in self:
                    x.append(hanger.tie_node.x)
                    n.append(hanger.effects_N[name]/1000)
                ax.plot(x, n, label=label, c=c, lw=lw, ls=ls)
            else:
                self.plot_effects(ax, name, key='Max', label=label, c=c, lw=lw, ls=ls)
                self.plot_effects(ax, name, key='Min', label=label, c=c, lw=lw, ls=ls)
        else:
            for hanger in self:
                x.append(hanger.tie_node.x)
                n.append(hanger.effects_N[name][key]/1000)
            ax.plot(x, n, label=label, c=c, lw=lw, ls=ls, marker="x")
        return
