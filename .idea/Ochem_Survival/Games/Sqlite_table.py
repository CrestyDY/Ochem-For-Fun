import sqlite3
import Organic_database_with_structure as dws
from io import BytesIO
from PIL import Image

# Connect to the database
ochem_database = sqlite3.connect('ochem.db')
cursor = ochem_database.cursor()

# Create the table if it doesn't exist
create_table_query = """
CREATE TABLE IF NOT EXISTS ochem_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chemical_formula TEXT NOT NULL,
    pH REAL NOT NULL,
    iupac TEXT NOT NULL,
    image_file BLOB NOT NULL
);
"""
cursor.execute(create_table_query)

# Prepare the insert query
insert_query = """
INSERT INTO ochem_table (chemical_formula, pH, iupac, image_file)
VALUES (?, ?, ?, ?);
"""

# Loop through the data and insert it
for compound in dws.struc_ls:
    chemical_formula = compound[0]
    pH = float(compound[1])
    iupac = compound[3]
    image = compound[4]

    # Convert the Image object to binary data
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='PNG')  # Save as PNG or the format you want
    img_byte_arr.seek(0)
    image_binary = img_byte_arr.read()  # Read the binary data

    # Insert the data into the table
    compound_data = (chemical_formula, pH, iupac, image_binary)
    cursor.execute(insert_query, compound_data)

# Commit and close the database connection
ochem_database.commit()
ochem_database.close()


