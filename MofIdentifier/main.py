from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.fileIO import LigandReader

if __name__ == '__main__':
    # uses https://pypi.org/project/PyCifRW/4.3/#description to read CIF files

    ligand = LigandReader.get_mol_from_file(input('Ligand?'))
    molecule = LigandReader.get_mol_from_file(input('Larger Molecule?'))
    print(SubGraphMatcher.find_ligand_in_mof(ligand, molecule))
    my_num = input('Enter a number')
