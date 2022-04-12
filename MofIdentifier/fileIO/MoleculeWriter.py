import os


def write_many(mols, path):
    if os.path.isdir(path):
        for mol in mols:
            write_one(mol, path)


def write_one(mol, path):
    if os.path.isdir(path):
        complete_path = os.path.join(path, mol.label)
        with open(complete_path, "w") as f:
            f.write(mol.file_content)
    else:
        raise ValueError(f'Target filepath {path} is not an existing directory')
