from pathlib import Path

from DAO import MOFDAO
from MofIdentifier.Molecules import atom
from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.fileIO import XyzReader

if __name__ == '__main__':
    containing_mofs = ["mof label, metal(s)"]
    total_freq = 0
    for mof_db in MOFDAO.get_mof_iterator():
        if 'MOM.xyz' in mof_db.ligand_names:
            total_freq += 1
            metals = [elem for elem in mof_db.elementsPresent if atom.is_metal(elem)]
            containing_mofs.append(f"{mof_db.filename}, {', '.join(metals)}")
    with open("output/contains_metal-oxygen-metal.csv", "w") as f:
        f.write('\n'.join(containing_mofs))
    print(total_freq)