from pathlib import Path

from DAOsAndServices import SBUDAO
from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.fileIO import LigandReader, XyzReader

if __name__ == '__main__':
    Carboxylate = XyzReader.get_molecule(str(Path(r'input/Carboxylate.xyz')))
    if Carboxylate is None:
        raise FileNotFoundError('Unable to get Carboxylate molecule from file')
    containing_connectors = ["connector label, frequency of connector in db"]
    total_freq = 0
    for sbu_db in SBUDAO.get_sbu_iterator():
        if sbu_db.type != 'connector':
            continue
        sbu = sbu_db.get_sbu()
        if SubGraphMatcher.find_ligand_in_mof(Carboxylate, sbu):
            total_freq += sbu_db.frequency
            containing_connectors.append(f"{sbu.label}, {sbu_db.frequency}")
    with open("output/contains_carboxylate.csv", "w") as f:
        f.write('\n'.join(containing_connectors))
    print(total_freq)