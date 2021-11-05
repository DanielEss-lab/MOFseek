import itertools
from collections import defaultdict

from Analysis import MOM
from DAO import MOFDAO
from MofIdentifier.Molecules import Atom
from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.fileIO import LigandReader


def create_file_of_MOFs_with_MOHMs():
    with open(r'C:\Users\mdavid4\Desktop\Esslab-P66\Analysis\input\MOHM.xyz', 'r') as MOHM_file:
        MOHM_string = MOHM_file.read()
    if MOHM_string is None or MOHM_string == '':
        raise FileNotFoundError('unable to get MOHM molecule')
    containing_mofs = ["mof label, metal(s)"]
    for mof_db in MOFDAO.get_mof_iterator():
        if 'MOHM.xyz' in mof_db.ligand_names:
            metals = [elem for elem in mof_db.elementsPresent if Atom.is_metal(elem)]
            MOHM_metal_strings = []
            for first_metal, second_metal in itertools.combinations_with_replacement(metals, 2):
                metal_string = f'{first_metal}-O(H)-{second_metal}'
                modified_MOHM = MOM.modify_MOM(MOHM_string, first_metal, second_metal, metal_string)
                if SubGraphMatcher.find_ligand_in_mof(modified_MOHM, mof_db.get_mof()):
                    MOHM_metal_strings.append(metal_string)
            assert len(MOHM_metal_strings) > 0
            containing_mofs.append(f"{mof_db.filename}, {', '.join(MOHM_metal_strings)}")
    with open("output/contains_MOHM.csv", "w") as f:
        f.write('\n'.join(containing_mofs))
    return len(containing_mofs) - 1


def create_file_of_MOHMs_and_frequencies():
    with open(r'C:\Users\mdavid4\Desktop\Esslab-P66\Analysis\output\contains_MOHM.csv', 'r') as MOHM_file:
        lines = MOHM_file.readlines()[1:]  # Cut out the labels at the top
    MOHMs_frequencies = defaultdict(lambda: 0)
    for line in lines:
        MOHMs = line.split(', ')[1:]  # Cut out the name of the mof
        for MOHM in MOHMs:
            if '\n' in MOHM:
                MOHM = MOHM.strip()
            MOHMs_frequencies[MOHM] += 1
    # format output:
    structure_freq_pairs = list(MOHMs_frequencies.items())
    structure_freq_pairs.sort(key=lambda pair: pair[0])
    lines = (f'{pair[0]}, {pair[1]}' for pair in structure_freq_pairs)
    with open("output/MOHMs_and_frequencies.csv", "w") as f:
        f.write('\n'.join(lines))
    return sum(MOHMs_frequencies.values())


if __name__ == '__main__':
    # freq_1 = create_file_of_MOFs_with_MOHMs()
    freq_1 = 636
    freq_2 = create_file_of_MOHMs_and_frequencies()
    if freq_1 != freq_2:
        print(f'{freq_1} frequency by MOFs but {freq_2} frequency by metal pairs, implying that some MOFs have multiple'
              f' kinds of metal-oxygen(H)-metal bonds')