import itertools

from MofIdentifier.Molecules.Atom import Atom
from MofIdentifier.bondTools import Distances, Angles


def is_bond_numbered_wca(element):\
    return (element[0] == '*' or element[0] == '&' or element[0] == '~') and len(element) > 1


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
            close_atoms = atom.bondedAtoms.copy()
            remove_distant_bonds(atom)
            # Adding the H to the second molecule might have broken a bond between molecules that should be bonded
            # now that the H is only bonded to one. Let's check that here:
            for atom_a, atom_b in itertools.combinations(close_atoms, 2):
                compare_for_bond(atom_a, atom_b)


def compare_for_bond(atom_a, atom_b):
    dist = Distances.distance(atom_a, atom_b)
    if is_bond_numbered_wca(atom_b.type_symbol):
        pass
    elif Distances.is_bond_distance(dist, atom_a, atom_b):
        if not is_blocked_bond(atom_a, atom_b):
            atom_a.bondedAtoms.append(atom_b)
            atom_b.bondedAtoms.append(atom_a)
            break_blocked_bonds(atom_a, atom_b)


def is_blocked_bond(atom_a, atom_b):
    # Sometimes two atoms are close enough that distance says they should be bonded, but from context they
    # clearly shouldn't be bonded, ie when they're bonded to another atom that's in between them.
    triangling_atoms = [atom for atom in atom_a.bondedAtoms if atom in atom_b.bondedAtoms]
    between_atoms = [atom for atom in triangling_atoms if
                     Angles.angle(atom_a, atom, atom_b) >
                     Angles.max_bond_breakup_angle]
    # The wider the angle, the more directly the connector is in between the metals.
    if len(between_atoms) > 0:
        angles = [Angles.angle(atom_a, a, atom_b) for a in between_atoms]
        angles.append(
            Angles.angle(atom_a, Atom.center_of(between_atoms, None), atom_b))
        if any(angle > Angles.bond_breakup_angle for angle in angles):
            return True
    return False


def break_blocked_bonds(atom_a, atom_b):
    # if adding a bond between atom a and atom b has caused a previously established bond to be blocked
    # (as per definition of blocked_bond() above), we need to undo that previous bond.
    triangling_atoms = [atom for atom in atom_a.bondedAtoms if atom in atom_b.bondedAtoms]
    for atom in triangling_atoms:
        if is_blocked_bond(atom_a, atom):
            atom_a.bondedAtoms.remove(atom)
            atom.bondedAtoms.remove(atom_a)
        elif is_blocked_bond(atom_b, atom):
            atom_b.bondedAtoms.remove(atom)
            atom.bondedAtoms.remove(atom_b)


def enfore_OCO_consistency(atoms):
    for atom in atoms:
        if atom.type_symbol == 'O' and len(atom.bondedAtoms) == 2:
            metals = [a for a in atom.bondedAtoms if a.is_metal()]
            carbons = [a for a in atom.bondedAtoms if a.type_symbol == 'C']
            if len(metals) != 1 or len(carbons) != 1:
                continue
            carbon = carbons[0]
            metal = metals[0]
            if len(carbon.bondedAtoms) == 3:
                other_oxygens = [a for a in carbon.bondedAtoms if a.type_symbol == 'O' and a.label != atom.label]
                if len(other_oxygens) != 1:
                    continue
                oxygen = other_oxygens[0]
            else:
                continue
            if metal not in oxygen.bondedAtoms and oxygen not in metal.bondedAtoms:
                distance = Distances.distance(metal, oxygen)
                required_distance = Distances.bond_distance(metal, oxygen,
                                                            Distances.bond_length_multiplicative_error_margin + 0.2)
                if distance <= required_distance:
                    oxygen.bondedAtoms.append(metal)
                    metal.bondedAtoms.append(oxygen)


def connect_atoms(molecule):
    atoms = molecule.atoms
    for i in range(len(atoms)):
        if is_bond_numbered_wca(atoms[i].type_symbol):
            make_numbered_bonds(i, atoms)
            continue
        for j in range(i+1, len(atoms)):
            compare_for_bond(atoms[i], atoms[j])
    enforce_single_hydrogen_bonds(atoms)
    enfore_OCO_consistency(atoms)
    return molecule
