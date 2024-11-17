import random as rd
import sqlite3 as sql
from io import BytesIO
from PIL import Image

#This gamemode will display 4 different compounds in bond line structure. User will pick the most acidic among them.
ochem_database = sql.connect('ochem.db')

cursor = ochem_database.cursor()

cursor.execute("SELECT MIN(id), MAX(id) FROM ochem_table;")
min_id, max_id = cursor.fetchone()

# Step 2: Generate 4 unique random numbers within the ID range
random_compounds = rd.sample(range(min_id, max_id + 1), 4)

extract_query = """
SELECT chemical_formula, pH, iupac, image_file FROM ochem_table
WHERE id IN (?,?,?,?);
"""

cursor.execute(extract_query, random_compounds)
my_compounds = cursor.fetchall()

ochem_database.commit()
ochem_database.close()

Correct_compound = my_compounds[0]
Wrong_compound1 = my_compounds[1]
Wrong_compound2 = my_compounds[2]
Wrong_compound3 = my_compounds[3]

image = Image.open(BytesIO(Correct_compound[3]))

Correct_image = Image.open(BytesIO(Wrong_compound1[3]))
Wrong_image1 = Image.open(BytesIO(Wrong_compound1[3]))
Wrong_image2 = Image.open(BytesIO(Wrong_compound2[3]))
Wrong_image3 = Image.open(BytesIO(Wrong_compound3[3]))

def Run_game():
    Correct_image.show()
    Wrong_image1.show()
    Wrong_image2.show()
    Wrong_image3.show()
Run_game()
