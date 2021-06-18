def atoms_to_xyz_string(atoms, filename):
    string = "{}\n{}\n".format(len(atoms), filename)
    for atom in atoms:
        string += ("{:4} {:11.6f} {:11.6f} {:11.6f}\n".format(atom.type_symbol, atom.x, atom.y, atom.z))
    return string


def write_molecule_to_file(filepath, molecule, filename):
    if molecule.file_content is None or len(molecule.file_content) == 0:
        molecule.file_content = atoms_to_xyz_string(molecule.atoms, filename)
    with open(filepath, 'w') as xyz:
        xyz.write(molecule.file_content)
