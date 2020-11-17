class CrossSection:
    def __init__(self, g, ea, ei, ga=0):
        self.weight = g
        self.axial_stiffness = ea
        self.bending_stiffness = ei
        self.shear_stiffness = ga
        return

    def get_beam(self):
        if self.shear_stiffness:
            beam = [self.axial_stiffness, self.bending_stiffness, self.shear_stiffness]
        else:
            beam = [self.axial_stiffness, self.bending_stiffness]
        return beam

    def get_self_weight(self, i):
        load = [i, 0, 0, 0, -self.weight, 0, 0, -self.weight, 0]
        return load
