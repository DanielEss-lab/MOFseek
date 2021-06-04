def write_molecule_to_file(filepath, atoms, filename):
    with open(filepath, 'w') as xyz:
        xyz.write("{}\n{}\n".format(len(atoms), filename))
        for atom in atoms:
            xyz.write("{:4} {:11.6f} {:11.6f} {:11.6f}\n".format(
                atom.type_symbol, atom.x, atom.y, atom.z))
