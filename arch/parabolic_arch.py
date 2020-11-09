from .arch import Arch
import numpy as np


class ParabolicArch(Arch):
    def __init__(self, rise, span, n):
        super().__init__(rise, span)

        radius = (rise ** 2 + (span / 2) ** 2) / (2 * rise)
        x_arch = list(np.linspace(0, span, 2 * n + 1))
        y_arch = [rise - radius * (1 - (1 - ((x - span / 2) / radius) ** 2) ** 0.5) for x in x_arch]

        self.coordinates = list(zip(x_arch, y_arch))
