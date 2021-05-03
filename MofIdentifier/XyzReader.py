import time
import pandas as pd
from MofIdentifier.Ligand import Ligand
from MofIdentifier.XyzBondCreator import XyzBondCreator
from MofIdentifier.atom import Atom


def read_xyz(file):
    molecule = pd.read_table(file, skiprows=2, delim_whitespace=True,
                             names=['atom', 'x', 'y', 'z'])
    atoms = list(())
    index = 0
    for atomData in molecule.values:
        atom = Atom(atomData[0] + str(index),
                    atomData[0],
                    float(atomData[1]),
                    float(atomData[2]),
                    float(atomData[3]))
        atoms.append(atom)
        index += 1
    return Ligand(file, atoms)


if __name__ == '__main__':
    # uses https://pypi.org/project/PyCifRW/4.3/#description to read CIF files

    before_read_time = time.time()
    ligand = read_xyz('Benzene.xyz')
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
