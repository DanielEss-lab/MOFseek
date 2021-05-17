def write_molecule_to_file(filename, atoms):
    with open(filename, 'w') as xyz:
        xyz.write("{}\n{}\n".format(len(atoms), filename))
        for atom in atoms:
            xyz.write("{:4} {:11.6f} {:11.6f} {:11.6f}\n".format(
                atom.type_symbol, atom.x, atom.y, atom.z))
