from pathlib import Path

from DAO import SBUDAO
from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.fileIO import LigandReader

if __name__ == '__main__':
    Carboxylate = LigandReader.get_mol_from_file(str(Path(r'C:\Users\mdavid4\Desktop\Esslab-P66\Analysis\input\Carboxylate.xyz')))
    if Carboxylate is None:
        raise Exception('Unable to get Carboxylate molecule from file')
    containing_connectors = []
    for sbu_db in SBUDAO.get_sbu_iterator():
        if sbu_db.type != 'connector':
            continue
        sbu = sbu_db.get_sbu()
        if SubGraphMatcher.find_ligand_in_mof(Carboxylate, sbu):
            containing_connectors.append(sbu.label)
    with open("output/contains_carboxylate.txt", "w") as f:
        f.write('\n'.join(containing_connectors))
