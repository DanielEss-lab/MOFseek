import itertools

import numpy as np

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


def undo_bad_metal_bonds(atoms):
    metals = (atom for atom in atoms if atom.is_metal())
    for metal_a, metal_b in itertools.combinations(metals, 2):
        if metal_a in metal_b.bondedAtoms:
            if blocked_bond(metal_a, metal_b):
                metal_a.bondedAtoms.remove(metal_b)
                metal_b.bondedAtoms.remove(metal_a)


def blocked_bond(metal_a, metal_b):
    for connecting_atom in metal_a.bondedAtoms:
        if connecting_atom.is_metal():
            continue
        if metal_b in connecting_atom.bondedAtoms:
            dist_a = Distances.distance(metal_a, connecting_atom)
            dist_b = Distances.distance(metal_b, connecting_atom)
            dist_c = Distances.distance(metal_a, metal_b)
            arccos_input = (dist_a ** 2 + dist_b ** 2 - dist_c ** 2) / (2 * dist_a * dist_b)
            if arccos_input > 1 or arccos_input < -1:
                continue
            c_angle = np.arccos(arccos_input)
            # The wider the angle, the more directly the connector is in between the metals.
            if c_angle > Distances.metal_bond_breakup_angle_margin:
                return True


def connect_atoms(molecule):
    atoms = molecule.atoms
    for i in range(len(atoms)):
        if is_bond_numbered_wca(atoms[i].type_symbol):
            make_numbered_bonds(i, atoms)
            continue
        for j in range(i+1, len(atoms)):
            compare_for_bond(atoms[i], atoms[j])
    enforce_single_hydrogen_bonds(atoms)
    undo_bad_metal_bonds(atoms)
    return molecule
