
from io import StringIO
from pathlib import Path

import pandas as pd

from MofIdentifier.Molecules.Ligand import Ligand
from MofIdentifier.Molecules.atom import Atom
from MofIdentifier.SubGraphMatching import CustomWildcard
from MofIdentifier.fileIO import XyzBondCreator


def get_molecule(filename):
    mol = read_xyz(filename)
    XyzBondCreator.connect_atoms(mol)
    return mol


def get_molecule_from_string(string, name):
    mol = read_string(string, name)
    XyzBondCreator.connect_atoms(mol)
    return mol


def read_xyz(file):
    atoms = get_atoms(file)
    file_str = Path(file).read_text()
    wildcards_line = file_str.split('\n')[1]
    wildcards = CustomWildcard.WC.parse_line(wildcards_line)
    return Ligand(file, atoms, file_str, wildcards)


def read_string(file_content, name):
    wildcards_line = file_content.split('\n')[1]
    wildcards = CustomWildcard.WC.parse_line(wildcards_line)
    atoms = get_atoms(StringIO(file_content))
    return Ligand(name, atoms, file_content, wildcards)


def get_atoms(file_like):
    molecule = pd.read_table(file_like, skiprows=2, delim_whitespace=True,
                             names=['atom', 'x', 'y', 'z'])
    atoms = list(())
    index = 0
    for atomData in molecule.values:
        symbol: str = atomData[0]
        if symbol.endswith('`'):
            symbol = symbol[0:-1]
            explicitly_open_to_more_bonds = True
        else:
            explicitly_open_to_more_bonds = False
        atom = Atom.from_cartesian(symbol + str(index),
                                   symbol,
                                   float(atomData[1]),
                                   float(atomData[2]),
                                   float(atomData[3]))
        if not explicitly_open_to_more_bonds:
            atom.is_bond_limited = True
        atoms.append(atom)
        index += 1
    return atoms


if __name__ == '__main__':
    file = '../ligands/M6_node.xyz'
    string = Path(file).read_text()
    print(read_string(string, 'name'))
    print(read_xyz(file))
