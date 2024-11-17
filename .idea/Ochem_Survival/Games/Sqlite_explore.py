import sqlite3 as sql
from io import BytesIO
from PIL import Image

user = sql.connect("ochem.db")
cursor = user.cursor()

query = """
SELECT image_file FROM ochem_table
WHERE iupac IN (?);
"""

Continue = True
while Continue:
    compound_name = input("What compound are you interested in ?\nIf you do not want to further research our database, enter 'END': ")
    if compound_name == 'END':
        Continue = False
        print("You have ended the session.")
    else:
        try:
            cursor.execute(query, (compound_name,))
            image = cursor.fetchone()
            if image:
                compound_image = Image.open(BytesIO(image[0]))
                compound_image.show()
                print("Query successful!")
            else:
                print("Query failed!")
        except sql.DatabaseError as error:
            print("An error occurred.")
