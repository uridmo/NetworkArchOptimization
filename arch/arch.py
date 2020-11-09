import numpy as np


class Arch:
    def __init__(self, span, rise):
        self.span = span
        self.rise = rise
        self.coordinates = None
        self.axial_stiffness = None
        self.bending_stiffness = None

    def arch_model(self):
        model = self.axial_stiffness
        return model

    def assign_stiffness(self, ea, ei):
        self.axial_stiffness = ea
        self.bending_stiffness = ei
        return

    def arch_connection_nodes(self, hangers):
        for j in range(len(hangers)):
            x_tie = hangers[j][0]
            angle = hangers[j][1]

            for i in range(len(self.coordinates) - 1):
                x_arch_1 = self.coordinates[i][0]
                x_arch_2 = self.coordinates[i+1][0]
                y_arch_1 = self.coordinates[i][1]
                y_arch_2 = self.coordinates[i+1][1]
                dx = x_arch_2 - x_arch_1
                dy = y_arch_2 - y_arch_1
                if angle == np.pi / 2:
                    if x_arch_1 < x_tie < x_arch_2:
                        x = x_tie
                        y = y_arch_1 + dy * (x_tie - x_arch_1) / dx
                        self.coordinates.insert(i+1, (x, y))
                        hangers[j].append(i + 1)
                        break
                else:
                    tan_a = np.tan(angle)
                    a = -(dy * tan_a * x_tie - dy * tan_a * x_arch_1 + dx * tan_a * y_arch_1) / (dy - dx * tan_a)
                    b = -(y_arch_1 - tan_a * x_arch_1 + tan_a * x_tie) / (dy - dx * tan_a)
                    if 0 <= b < 1 and a > 0:
                        x = x_arch_1 + b * dx
                        y = y_arch_1 + b * dy
                        self.coordinates.insert(i+1, (x, y))
                        hangers[j].append(i + 1)
                        break

        # Adapt the nodes for the inserted points
        for j in range(len(hangers) - 1):
            for i in range(j + 1, len(hangers)):
                if hangers[j][2] >= hangers[i][2]:
                    hangers[i][2] += 1

        # Round the components of the nodes
        self.coordinates = [(round(x, 3), round(y, 3)) for x, y in self.coordinates]

        # Pop identical nodes
        x_prev = self.coordinates[0][0]
        for i, coord in enumerate(self.coordinates[1:]):
            if coord[0] == x_prev:
                self.coordinates.pop(i + 1)
                for hanger in hangers:
                    if hanger[2] >= i + 1:
                        hanger[2] -= 1
        return hangers
