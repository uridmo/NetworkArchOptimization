import os


def table_from_cross_sections(directory, name, cross_sections):
    if not os.path.isdir(directory):
        os.makedirs(directory)

    text = open(directory+"/"+name+".txt", 'w')
    text.write(r"\begin{table}[H] "+"\n")
    text.write(r"\begin{tabular}{llcccc}"+"\n")
    text.write(r"\hline"+"\n")
    text.write(r"Region & Limit state & Normal force & Moment-y & Moment-z & Demand/Capacity \\"+"\n")
    text.write(r" & & [MN]   & [MNm] & [MNm] & [-] \\ \hline"+"\n")
    for cs in cross_sections:
        name = cs.name
        p_i = cs.effects['Strength-I']['Normal Force'][2]
        mz_i = cs.effects['Strength-I']['Moment'][2]
        my_i = cs.effects['Strength-I']['Moment y'][2]
        p_iii = cs.effects['Strength-III']['Normal Force'][2]
        mz_iii = cs.effects['Strength-III']['Moment'][2]
        my_iii = cs.effects['Strength-III']['Moment y'][2]
        p_cl = 0
        mz_cl = 0
        my_cl = 0

        d_c_i = cs.degree_of_compliance['Strength-I']
        d_c_iii = cs.degree_of_compliance['Strength-III']
        d_c_cl = 0

        text.write(r"\multirow{3}{*}{"+name+"}"+f" & Strength-I & {p_i:.0f} & {mz_i:.0f} & {my_i:.0f} & "+f"{d_c_i:.2f}"+r"\\"+"\n")
        text.write(f" & Strength-III & {p_iii:.0f} & {mz_iii:.0f} & {my_iii:.0f} & "+f"{d_c_iii:.2f}"+r"\\"+"\n")
        text.write(f" & Cable loss & {p_cl:.0f} & {mz_cl:.0f} & {my_cl:.0f} & "+f"{d_c_cl:.2f}"+r"\\ \hline"+"\n")
    text.write(r"\end{tabular}" + "\n")
    text.write(r"\end{table}" + "\n")

    text.close()
    return
