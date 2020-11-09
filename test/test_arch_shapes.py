from arch.arch import Arch
from arch.parabolic_arch import ParabolicArch


a = Arch(4, 5)
b = ParabolicArch(5, 6, 8)
print(a.bending_stiffness)
print(b.coordinates)
