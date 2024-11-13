import bond_line_conv as chem
import sorted_by_pKa

struc_ls = sorted_by_pKa.sorted_ls
for i in range(len(struc_ls)):
    formula = struc_ls[i][0]
    iupac = struc_ls[i][3]
    structure = chem.formula_to_structure(formula, iupac)
    struc_ls[i].append(structure)
    struc_ls[i].append(str(structure))
x = "Chemical Formula: {:141s} pKa: {:7s} Temperature: {:10s} Iupac Name: {:143s} Structure: {:80s}"
with open("output.txt", "w") as f:
    for i in range(len(struc_ls)):
        print(x.format(struc_ls[i][0],struc_ls[i][1],struc_ls[i][2],struc_ls[i][3], struc_ls[i][5]), file=f)
struc_ls[0][4].show()

"""x = "Chemical Formula: {:141s} pKa: {:7s} Temperature: {:10s} Iupac Name: {:143s} Structure: {:80s}"
for j in range(len(struc_ls)):
    print(x.format(struc_ls[j][0],struc_ls[j][1],struc_ls[j][2],struc_ls[j][3], struc_ls[j][5]))"""

