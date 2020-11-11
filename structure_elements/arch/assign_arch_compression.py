
def define_by_peak_moment(arch, nodes, hangers, mz_0, peak_moment=0):
    arch.calculate_permanent_impacts(nodes, hangers, 0, mz_0)
    moments_arch = arch.impacts['Permanent']['Moment']
    moment_max = max([max(moments) for moments in moments_arch])
    compression_force = (moment_max-peak_moment)/arch.rise
    return compression_force
