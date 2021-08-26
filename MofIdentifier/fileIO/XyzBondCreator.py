from MofIdentifier.bondTools import Distances


def is_bond_numbered_wca(element):\
    return (element[0] == '*' or element[0] == '%' or element[0] == '#') and len(element) > 1


def make_numbered_bonds(i, atoms):
    # Connect atoms[i] to the n closest atoms
    num_bonds = int(atoms[i].type_symbol[1])

    other_atoms = [(Distances.distance(atoms[i], atoms[j]), j) for j in range(len(atoms)) if i != j]
    sorted_distances = sorted(other_atoms, key=lambda x: x[0])
    for dist_index in range(num_bonds):
        j = sorted_distances[dist_index][1]
        atoms[i].bondedAtoms.append(atoms[j])
        atoms[j].bondedAtoms.append(atoms[i])


def remove_distant_bonds(atom):
    lowest_distance = float('inf')
    closest_atom = None
    for neighbor in atom.bondedAtoms:
        distance = Distances.distance(atom, neighbor)
        if distance < lowest_distance:
            lowest_distance = distance
            closest_atom = neighbor
    for neighbor in atom.bondedAtoms.copy():
        if neighbor != closest_atom:
            neighbor.bondedAtoms.remove(atom)
            atom.bondedAtoms.remove(neighbor)


def enforce_single_hydrogen_bonds(atoms):
    for atom in atoms:
        if atom.type_symbol == 'H' and len(atom.bondedAtoms) > 1:
            remove_distant_bonds(atom)


def compare_for_bond(atom_a, atom_b):
    dist = Distances.distance(atom_a, atom_b)
    if is_bond_numbered_wca(atom_b.type_symbol):
        pass
    elif Distances.is_bond_distance(dist, atom_a, atom_b):
        atom_a.bondedAtoms.append(atom_b)
        atom_b.bondedAtoms.append(atom_a)


def connect_atoms(molecule):
    atoms = molecule.atoms
    for i in range(len(atoms)):
        if is_bond_numbered_wca(atoms[i].type_symbol):
            make_numbered_bonds(i, atoms)
            continue
        for j in range(i+1, len(atoms)):
            compare_for_bond(atoms[i], atoms[j])
    enforce_single_hydrogen_bonds(atoms)
    return molecule
