from rdkit import Chem
from rdkit.Chem import Draw
from PIL import Image, ImageDraw, ImageFont
import random
import Organic_sorted_by_pKa as sbp

from rdkit import Chem
from rdkit.Chem import Draw
from PIL import Image


def formula_to_structure(formula, molecule_name="Molecule"):
    # Convert the SMILES formula to a molecule object
    mol = Chem.MolFromSmiles(formula)

    if mol:
        # Create the molecule image
        mol_img = Draw.MolToImage(mol)

        # Return the molecule image
        return mol_img
    else:
        print(f"Invalid formula: {formula}")
        return None


"""x = random.randint(1, 100)
structure_test = formula_to_structure(sbp.sorted_ls[x][0], sbp.sorted_ls[x][3])


if structure_test:
    structure_test.show()  # Display the generated image if successful
else:
    print("Invalid SMILES string")"""
