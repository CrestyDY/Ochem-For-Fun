from rdkit import Chem
from rdkit.Chem import Draw
from PIL import Image, ImageDraw, ImageFont
import random
import sorted_by_pKa as sbp


def formula_to_structure(formula, molecule_name="Molecule"):
    mol = Chem.MolFromSmiles(formula)
    if mol:
        # Create molecule image
        mol_img = Draw.MolToImage(mol)

        # Define font and image for the label (adjust font size as needed)
        img_width, img_height = mol_img.size
        font_size = 20
        try:
            font = ImageFont.truetype("arial.ttf", font_size)  # Specify the font path if needed
        except IOError:
            font = ImageFont.load_default()  # Use default font if custom font is not found

        # Create a new image with space for the text
        total_height = img_height + font_size + 10
        new_img = Image.new("RGB", (img_width, total_height), color="white")

        # Paste the molecule image onto the new ima(ge
        new_img.paste(mol_img, (0, 0))

        # Draw the text (molecule name) below the image
        draw = ImageDraw.Draw(new_img)
        bbox = draw.textbbox((0, 0), molecule_name, font=font)  # Get the bounding box of the text
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]  # Calculate width and height of text
        text_position = ((img_width - text_width) // 2, img_height + 5)  # Center text under the image
        draw.text(text_position, molecule_name, font=font, fill="black")

        return new_img
    else:
        return None
"""x = random.randint(1, 100)
structure_test = formula_to_structure(sbp.sorted_ls[x][0], sbp.sorted_ls[x][3])


if structure_test:
    structure_test.show()  # Display the generated image if successful
else:
    print("Invalid SMILES string")"""
