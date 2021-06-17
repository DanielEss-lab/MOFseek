import time
from io import FileIO
from pathlib import Path

import pandas as pd
from MofIdentifier.Molecules.Ligand import Ligand
from MofIdentifier.fileIO.XyzBondCreator import XyzBondCreator
from MofIdentifier.Molecules.atom import Atom

bond_creator = XyzBondCreator()


def get_molecule(filename):
    mol = read_xyz(filename)
    bond_creator.connect_atoms(mol)
    return mol


def read_xyz(file):
    molecule = pd.read_table(file, skiprows=2, delim_whitespace=True,
                             names=['atom', 'x', 'y', 'z'])
    file_str = Path(file).read_text()
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
    return Ligand(file, atoms, file_str)


if __name__ == '__main__':
    # uses https://pypi.org/project/PyCifRW/4.3/#description to read CIF files

    before_read_time = time.time()
    ligand = read_xyz('../ligands/test_resources/Benzene.xyz')
    between_time = time.time()
    bond_creator = XyzBondCreator()
    bond_creator.connect_atoms(ligand)
    numBonds, numCompared = bond_creator.get_extra_information()
    end_time = time.time()

    print('number of atoms: {}'.format(len(ligand.atoms)))
    print('number of bonds determined to exist: {}'.format(numBonds))
    print('number of atom comparisons made: {}'.format(numCompared))
    possibleComparisons = len(ligand.atoms) ** 2
    print('num comparisons in a naive approach: {}'.format(possibleComparisons))
    print('time to read from cif: {}'.format(between_time - before_read_time))
    print('time for algorithm to run on mof: {}'.format(end_time - between_time))
    print('\n\tAtoms and their bonds:')
    print(*ligand.atoms, sep="\n")
