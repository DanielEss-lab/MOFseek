from MofIdentifier.Molecules import Molecule
from MofIdentifier.SubGraphMatching import SubGraphMatcher


def get_connected_components(atoms):
    connected_components = list()
    visited_labels = set()
    for atom in atoms:
        if atom.label not in visited_labels:
            group = list()
            add_reachables_to_group(atom, group, visited_labels)
            connected_components.append(group)
    connected_components.sort(key=lambda g: len(g), reverse=True)
    return connected_components


def add_reachables_to_group(atom, group, visited_labels):
    group.append(atom)
    visited_labels.add(atom.label)
    for neighbor in atom.bondedAtoms:
        if neighbor.label not in visited_labels:
            add_reachables_to_group(neighbor, group, visited_labels)


def count_solvents(atom_groups):
    solvents = [Molecule.Molecule('solvent: no filepath', group) for group in atom_groups]
    new_groups_list = dict()
    i = 0
    while i < len(solvents):
        new_groups_list[solvents[i]] = 1
        j = i + 1
        while j < len(solvents):
            if SubGraphMatcher.mol_are_isomorphic(solvents[i], solvents[j]):
                new_groups_list[solvents[i]] += 1
                solvents.pop(j)
            else:
                j += 1
        i += 1
    return new_groups_list
