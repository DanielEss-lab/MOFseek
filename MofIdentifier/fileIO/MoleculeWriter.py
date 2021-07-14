import os


def write_many(mols, path):
    if len(mols) == 0:
        return
    if path is None:
        return
    for mol in mols:
        write_one(mol, path)


def write_one(mol, path):
    with open(os.path.join(path, mol.label), "w") as f:
        f.write(mol.file_content)