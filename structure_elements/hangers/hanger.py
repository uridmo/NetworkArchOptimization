import numpy as np


class Hanger:
    def __init__(self, tie_node, angle):
        self.tie_node = tie_node
        self.arch_node = None
        self.inclination = angle
        self.prestressing_force = None
        self.axial_stiffness = None
        self.bending_stiffness = None
        self.effects_N = {}
        self.effects_range_N = {}
        return

    def __repr__(self):
        string = '(Tie: '+str(self.tie_node)
        string += ', Angle: ' + str(round(np.rad2deg(self.inclination), 1))+')'
        return string

    def length(self):
        dx = self.tie_node.x - self.arch_node.x
        dy = self.tie_node.y - self.arch_node.y
        dl = (dx ** 2 + dy ** 2) ** 0.5
        return dl
