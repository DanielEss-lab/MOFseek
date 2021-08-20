
from io import StringIO
from pathlib import Path

import pandas as pd

from MofIdentifier.Molecules.Ligand import Ligand
from MofIdentifier.Molecules.atom import Atom
from MofIdentifier.fileIO.XyzBondCreator import XyzBondCreator

bond_creator = XyzBondCreator()


def get_molecule(filename):
    mol = read_xyz(filename)
    bond_creator.connect_atoms(mol)
    return mol


def get_molecule_from_string(string, name):
    mol = read_string(string, name)
    bond_creator.connect_atoms(mol)
    return mol


def read_xyz(file):
    atoms = get_atoms(file)
    file_str = Path(file).read_text()
    return Ligand(file, atoms, file_str)


def read_string(file_content, name):
    atoms = get_atoms(StringIO(file_content))
    return Ligand(name, atoms, file_content)


def get_atoms(file_like):
    molecule = pd.read_table(file_like, skiprows=2, delim_whitespace=True,
                             names=['atom', 'x', 'y', 'z'])
    atoms = list(())
    index = 0
    for atomData in molecule.values:
        atom = Atom.from_cartesian(atomData[0] + str(index),
                                   atomData[0],
                                   float(atomData[1]),
                                   float(atomData[2]),
                                   float(atomData[3]))
        atoms.append(atom)
        index += 1
    return atoms


if __name__ == '__main__':
    file = '../ligands/M6_node.xyz'
    string = Path(file).read_text()
    print(read_string(string, 'name'))
    print(read_xyz(file))
