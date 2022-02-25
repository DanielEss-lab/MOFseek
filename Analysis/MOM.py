import itertools
from collections import defaultdict
from pathlib import Path

from DAOsAndServices import MOFDAO
from MofIdentifier.Molecules import Atom
from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.fileIO import XyzReader, LigandReader


def modify_MOM(MOM_string, first_metal, second_metal, metal_string):
    ligand = LigandReader.get_mol_from_string(MOM_string.replace('&', first_metal, 1).replace(
                    '&', second_metal, 1), metal_string)
    for atom in ligand.atoms:
        if atom.is_metal():
            for neighbor in atom.bondedAtoms:
                if neighbor.is_metal():
                    atom.bondedAtoms.remove(neighbor)
                    neighbor.bondedAtoms.remove(atom)
    for atom in ligand.atoms:
        if atom.type_symbol == 'O':
            for other_atom in ligand.atoms:
                if other_atom.type_symbol != 'O' and other_atom not in atom.bondedAtoms:
                    atom.bondedAtoms.append(other_atom)
                    other_atom.bondedAtoms.append(atom)
    return ligand


def create_file_of_MOFs_with_MOMs():
    with open(r'C:\Users\mdavid4\Desktop\Esslab-P66\Analysis\input\MOM.xyz', 'r') as MOM_file:
        MOM_string = MOM_file.read()
    if MOM_string is None or MOM_string == '':
        raise FileNotFoundError('unable to get MOM molecule')
    containing_mofs = ["mof label, metal(s)"]
    for mof_db in MOFDAO.get_mof_iterator():
        if 'MOM.xyz' in mof_db.ligand_names:
            metals = [elem for elem in mof_db.elementsPresent if Atom.is_metal(elem)]
            MOM_metal_strings = []
            for first_metal, second_metal in itertools.combinations_with_replacement(metals, 2):
                metal_string = f'{first_metal}-O-{second_metal}'
                modified_MOM = modify_MOM(MOM_string, first_metal, second_metal, metal_string)
                if SubGraphMatcher.find_ligand_in_mof(modified_MOM, mof_db.get_mof()):
                    MOM_metal_strings.append(metal_string)
            assert len(MOM_metal_strings) > 0
            containing_mofs.append(f"{mof_db.filename}, {', '.join(MOM_metal_strings)}")
    with open("output/contains_MOM.csv", "w") as f:
        f.write('\n'.join(containing_mofs))
    return len(containing_mofs) - 1


def create_file_of_MOMs_and_frequencies():
    with open(r'C:\Users\mdavid4\Desktop\Esslab-P66\Analysis\output\contains_MOM.csv', 'r') as MOM_file:
        lines = MOM_file.readlines()[1:]  # Cut out the labels at the top
    MOMs_frequencies = defaultdict(lambda: 0)
    for line in lines:
        MOMs = line.split(', ')[1:]  # Cut out the name of the mof
        for MOM in MOMs:
            if '\n' in MOM:
                MOM = MOM.strip()
            MOMs_frequencies[MOM] += 1
    # format output:
    structure_freq_pairs = list(MOMs_frequencies.items())
    structure_freq_pairs.sort(key=lambda pair: pair[0])
    lines = (f'{pair[0]}, {pair[1]}' for pair in structure_freq_pairs)
    with open("output/MOMs_and_frequencies.csv", "w") as f:
        f.write('\n'.join(lines))
    return sum(MOMs_frequencies.values())


if __name__ == '__main__':
    # freq_1 = create_file_of_MOFs_with_MOMs()
    freq_1 = 3630
    freq_2 = create_file_of_MOMs_and_frequencies()
    if freq_1 != freq_2:
        print(f'{freq_1} frequency by MOFs but {freq_2} frequency by metal pairs, implying that some MOFs have multiple'
              f' kinds of metal-oxygen-metal bonds')
