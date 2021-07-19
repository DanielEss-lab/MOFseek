import os

from MofIdentifier.bondTools import SolventTools


def write_without_solvent(mol, path):
    file_content = SolventTools.get_file_content_without_solvents(mol)
    if os.path.isdir(path):
        complete_path = os.path.join(path, mol.label)
        if not os.path.exists(complete_path):
            with open(complete_path, "w") as f:
                f.write(file_content)
