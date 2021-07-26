from MofIdentifier.bondTools import Distances

MINIMUM_BOND_DISTANCE = 0.7


class IrreparableMofError(Exception):
    pass


def clean(mof):
    num_corrections = 0
    try:
        while True:
            for atom in mof.atoms:
                if atom.type_symbol == 'H' and any(neighbor.type_symbol == 'H' for neighbor in atom.bondedAtoms):
                    mof = fix_connected_hydrogens(mof, atom)
                    num_corrections += 1
                    continue
            for atom in mof.atoms:
                if atom.type_symbol == 'H' and len(atom.bondedAtoms) > 1:
                    mof = fix_overconnected_hydrogen(mof, atom)
                    num_corrections += 1
                    continue
            for atom in mof.atoms:
                if atom.type_symbol == 'C' and len(atom.bondedAtoms) == 1:
                    mof = fix_underconnected_carbon(mof, atom)
                    num_corrections += 1
                    continue
            for atom in mof.atoms:
                for neighbor in atom.bondedAtoms:
                    if Distances.distance(atom, neighbor) < MINIMUM_BOND_DISTANCE:
                        mof = fix_atoms_too_close(mof, atom)
                        continue
            return True
    except IrreparableMofError:
        return False


def fix_connected_hydrogens(mof, starting_atom):
    assert(starting_atom.type_symbol == 'H')
    least_connected_atom = starting_atom
    for neighbor in starting_atom.bondedAtoms:
        if neighbor.type_symbol == 'H' and len(neighbor.bondedAtoms) < len(least_connected_atom.bondedAtoms):
            least_connected_atom = neighbor
    return mof.without_atom(least_connected_atom)


def fix_overconnected_hydrogen(mof, atom):
    pass


def fix_underconnected_carbon(mof, atom):
    pass


def fix_atoms_too_close(mof, atom):
    pass
    # if all too-closes in region are same-element duplicates:
    #           fix_wobble(mof, atoms):
    #       else:
    #           fix_poorly_placed_functional_groups()


def fix_wobble(mof, atom):
    pass


def fix_poorly_placed_functional_groups():
    pass
