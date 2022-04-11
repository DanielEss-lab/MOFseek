import os

from DAOsAndServices import SBUDAO
from GUI import Settings
from MofIdentifier.fileIO import SmilesWriter
import pandas as pd
from rdkit import Chem
from rdkit.Chem import PandasTools


def write_lists(name, name_endings, print_lists):
    for name_ending, print_list in zip(name_endings, print_lists):
        with open(f"{name}{name_ending}.csv", "w") as f:
            f.write('\n'.join(f'{tup[0]}, {tup[1]}, {tup[2]}, {tup[3]}' for tup in print_list))
        data = pd.read_csv("freq_connector.csv")
        data['Mol Image'] = [Chem.MolFromSmiles(s) for s in data[' smiles representation']]  # this is to generate image using SMILES
        PandasTools.SaveXlsxFromFrame(data[data['Mol Image'].notnull()], f'{name}{name_ending}_w_images.xlsx',
                                      molCol='Mol Image', size=(100, 100))  # this saves the image to Excel sheet
        data[data['Mol Image'].isnull()].to_csv(f"{name}{name_ending}_w_issues.csv", index=False)  # this saves the problematic ones


def get_frequencies():
    output_nodes = [("name", "frequency", "size (number of atoms)", "approximate smiles representation")]
    output_conns = [("name", "frequency", "size (number of atoms)", "approximate smiles representation")]
    output_auxs = [("name", "frequency", "size (number of atoms)", "approximate smiles representation")]
    for sbu in SBUDAO.get_sbu_iterator():
        freq = sbu.get_enabled_frequency()
        num_atoms = sbu.get_num_atoms()
        smiles_representation = SmilesWriter.get_smiles(sbu)
        if freq > 0:
            if sbu.type == 'cluster':
                output_nodes.append((sbu.name, freq, num_atoms, smiles_representation))
            elif sbu.type == 'connector':
                output_conns.append((sbu.name, freq, num_atoms, smiles_representation))
            elif sbu.type == 'auxiliary':
                output_auxs.append((sbu.name, freq, num_atoms, smiles_representation))
    return output_nodes, output_conns, output_auxs


def export_sbus():
    name_endings = ['node', 'connector', 'auxiliary']
    print_lists = get_frequencies()
    try:
        write_lists(os.path.join(Settings.get_download_filepath(), "freq_"), name_endings, print_lists)
    except PermissionError:
        raise RuntimeError("PermissionError when writing to file; make sure the file isn't open in any application")
