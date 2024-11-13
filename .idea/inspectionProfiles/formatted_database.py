import my_database

temp_string = [str(i) for i in my_database.data_temperature]
pKa_string = [str(i) for i in my_database.data_pKa]

x = "Chemical Formula: {:141s} pKa: {:7s} Temperature: {:10s} Iupac Name: {:143s}"
"""for i in range(len(my_database.final_data)):
    print(x.format(my_database.data_formula[i], pKa_string[i], temp_string[i], my_database.data_iupac[i]))"""