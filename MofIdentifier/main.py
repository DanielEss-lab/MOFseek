import time
import MofReader
from BondCreator import BondCreator

if __name__ == '__main__':
    # uses https://pypi.org/project/PyCifRW/4.3/#description to read CIF files

    before_read_time = time.time()
    mof = MofReader.read_mof('smod7-pos-1.cif')
    between_time = time.time()
    bond_creator = BondCreator(mof)
    bond_creator.connect_atoms()
    numBonds, numCompared = bond_creator.get_extra_information()
    end_time = time.time()

    print('number of atoms: {}'.format(len(mof.atoms)))
    print('number of bonds determined to exist: {}'.format(numBonds))
    print('number of atom comparisons made: {}'.format(numCompared))
    possibleComparisons = len(mof.atoms)**2
    print('num comparisons in a naive approach: {}'.format(possibleComparisons))
    print('time to read from cif: {}'.format(between_time - before_read_time))
    print('time for algorithm to run on mof: {}'.format(end_time - between_time))
    print('\n\tAtoms and their bonds:')
    print(*mof.atoms, sep="\n")
