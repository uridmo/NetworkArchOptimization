import os


def uls_forces_table(directory, name, cross_sections, all_uls=False):
    if not os.path.isdir(directory):
        os.makedirs(directory)

    text = open(directory+"/"+name+".txt", 'w')
    text.write(r"\begin{tabular}{llcccc}"+"\n")
    text.write(r"\hline"+"\n")
    text.write(r"Segment & Limit state & Normal force & Moment-y & Moment-z & Demand/Capacity \\"+"\n")
    text.write(r" & & [MN]   & [MNm] & [MNm] & [-] \\ \hline"+"\n")
    for cs in cross_sections:
        name = cs.name
        length = len(cs.effects)
        if all_uls:
            text.write(r"\multirow{"+str(length+1)+"}{*}{"+name+"}")
        else:
            text.write(r"\multirow{2}{*}{"+name+"}")

        dc_max = 0
        uls_max = ''
        for uls_type in cs.effects:
            p = cs.effects[uls_type]['Normal Force'][2]/1000
            mz = cs.effects[uls_type]['Moment'][2]/1000 if 'Moment' in cs.effects[uls_type] else 0
            my = cs.effects[uls_type]['Moment y'][2]/1000 if 'Moment y' in cs.effects[uls_type] else 0
            d_c = cs.degree_of_compliance[uls_type]
            if d_c > dc_max:
                dc_max = d_c
                uls_max = uls_type
            if all_uls:
                text.write(" & " + uls_type + f" & {p:.1f} & {mz:.1f} & {my:.1f} & " + f"{d_c:.2f}" + r"\\" + "\n")

        if not all_uls:
            p = cs.effects[uls_max]['Normal Force'][2] / 1000
            mz = cs.effects[uls_max]['Moment'][2] / 1000 if 'Moment' in cs.effects[uls_type] else 0
            my = cs.effects[uls_max]['Moment y'][2] / 1000 if 'Moment y' in cs.effects[uls_type] else 0
            d_c = cs.degree_of_compliance[uls_max]
            text.write(" & " + uls_max + f" & {p:.1f} & {mz:.1f} & {my:.1f} & " + f"{d_c:.2f}" + r"\\" + "\n")

        p_cl = 0
        mz_cl = 0
        my_cl = 0
        d_c_cl = 0

        text.write(f" & Cable loss & {p_cl:.1f} & {mz_cl:.1f} & {my_cl:.1f} & "+f"{d_c_cl:.2f}"+r"\\ \hline"+"\n")
    text.write(r"\end{tabular}" + "\n")

    text.close()
    return


def dc_table(directory, name, cross_sections, uls_types=""):
    if not os.path.isdir(directory):
        os.makedirs(directory)
    if not uls_types:
        uls_types = list(cross_sections[0].degree_of_compliance.keys())

    n = len(uls_types)
    text = open(directory + "/" + name + ".txt", 'w')
    text.write(r"\begin{tabular}{c"+"c"*(n+1)+"l}" + "\n")
    text.write(r"\hline" + "\n")
    text.write(r"Segment & \multicolumn{"+str(n+1)+r"}{c}{Demand / Capacity} & \\" + "\n")

    for uls_type in uls_types:
        text.write(" & "+uls_type)
    text.write(r" & Base case & \\ \hline"+"\n")

    for cs in cross_sections:
        text.write(cs.name)
        dcs = []
        for uls_type in uls_types:
            if uls_type not in cs.degree_of_compliance:
                dc = 0
            else:
                dc = cs.degree_of_compliance[uls_type]
            dcs.append(dc)
        for dc in dcs:
            if dc == max(dcs):
                text.write(r" & \textbf{"+f"{dc:.2f}"+r"}")
            else:
                text.write(f" & {dc:.2f}")
        text.write(r" & \textbf{"+f"{cs.dc_ref:.2f}"+r"} & (" + cs.load_ref + r") \\" + "\n")

    text.write(r"\hline" + "\n")
    text.write(r"\end{tabular}" + "\n")
    text.close()
    return


def cost_table(directory, name, cross_sections, anchorages):
    if not os.path.isdir(directory):
        os.makedirs(directory)

    text = open(directory + "/" + name + ".txt", 'w')
    text.write(r"\begin{tabular}{lcccccc}" + "\n")
    text.write(r"\hline" + "\n")
    text.write(r"Segment & Length & Weight & Unit cost & D/C$_{max}$ & D/C$_{ref}$ & Cost \\" + "\n")
    text.write(r" & [m] & [kg/m] & [\$/kg] & [-] & [-] & [\$ Mio.] \\ \hline" + "\n")

    costs = 50000
    for cs in cross_sections:
        name = cs.name
        length = cs.length
        unit_cost = cs.unit_cost
        unit_weight = cs.unit_weight
        dc_ref = cs.dc_ref
        dc_max = cs.dc_max
        cost = cs.cost
        costs += cost
        text.write(name+' & '+f"{length:.0f}"+' & '+f"{unit_weight:.0f}"+' & '+f"{unit_cost:.1f}")
        text.write(' & '+f"{dc_max:.2f}"+' & '+f"{dc_ref:.2f}"+' & '+f"{cost/10**6:.2f}"+r" \\" + "\n")

    text.write(r"\arrayrulecolor{gray} \hline" + "\n")
    text.write("- Anchorages & "+str(anchorages[0])+" ea & "+f"{anchorages[1]:.0f}"+' kg/ea & '+f"{anchorages[2]:.1f}")
    text.write(r" \$/kg & "+f"{dc_max:.2f}"+' & '+f"{dc_ref:.2f}"+' & '+f"{anchorages[3]/10**6:.2f}"+r" \\" + "\n")
    text.write(r"- Testing & - & - & 50000 \$ & - & - & 0.05 \\ \hline" + "\n")
    costs += anchorages[3]
    text.write("& & & & & & "+f"{costs/10**6:.2f}"+r" \\ \hhline{~~~~~~ =}"+"\n")
    text.write(r"\end{tabular}" + "\n")
    text.close()
    return
