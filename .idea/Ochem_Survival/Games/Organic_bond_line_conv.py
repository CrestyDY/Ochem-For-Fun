from rdkit import Chem
from rdkit.Chem import Draw
from PIL import Image, ImageDraw, ImageFont
import random
import Organic_sorted_by_pKa as sbp
from rdkit import Chem
from rdkit.Chem import Draw
from PIL import Image


def formula_to_structure(formula, molecule_name="Molecule"):
    mol = Chem.MolFromSmiles(formula)

    if mol:
        mol_img = Draw.MolToImage(mol)

        return mol_img
    else:
        print(f"Invalid formula: {formula}")
        return None

