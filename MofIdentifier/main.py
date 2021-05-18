import time
from MofIdentifier.fileIO import CifReader
from MofIdentifier.fileIO.MofBondCreator import MofBondCreator


if __name__ == '__main__':
    # uses https://pypi.org/project/PyCifRW/4.3/#description to read CIF files

    before_read_time = time.time()
    mof = CifReader.read_cif('mofsForTests/smod7-pos-1.cif')
    between_time = time.time()
    bond_creator = MofBondCreator(mof)
    bond_creator.connect_atoms()
    numBonds, numCompared, num_across_cell = bond_creator.get_extra_information()
    end_time = time.time()

    print('number of atoms: {}'.format(len(mof.atoms)))
    print('number of bonds determined to exist: {}'.format(numBonds))
    print('number of atom comparisons made: {}'.format(numCompared))
    print('number of above bonds that cross cell border: {}'.format(num_across_cell))
    print('time to read from cif: {}'.format(between_time - before_read_time))
    print('time for algorithm to run on mof: {}'.format(end_time - between_time))
    print('\n\tAtoms and their bonds:')
    print(*mof.atoms, sep="\n")

    for atom in mof.atoms:
        if atom.type_symbol == 'H':
            assert len(atom.bondedAtoms) == 1
        else:
            assert len(atom.bondedAtoms) > 0