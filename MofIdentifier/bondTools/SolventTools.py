from MofIdentifier.Molecules import Molecule
from MofIdentifier.SubGraphMatching import SubGraphMatcher
from collections import deque


def get_connected_components(atoms):
    connected_components = list()
    visited_labels = set()
    for atom in atoms:
        if atom.label not in visited_labels:
            group = gather_all_connected_atoms(atom, visited_labels)
            connected_components.append(group)
    connected_components.sort(key=lambda g: len(g), reverse=True)
    return connected_components


def gather_all_connected_atoms(atom, visited_labels):
    group = list()
    atoms_to_visit = deque()
    atoms_to_visit.append(atom)
    while len(atoms_to_visit) > 0:
        atom = atoms_to_visit.popleft()
        if atom.label in visited_labels:
            continue
        group.append(atom)
        visited_labels.add(atom.label)
        for neighbor in atom.bondedAtoms:
            if neighbor.label not in visited_labels:
                atoms_to_visit.append(neighbor)
    return group


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


def get_file_content_without_solvents(mof):
    if len(mof.solvents) == 0:
        return mof.file_content
    file_content: str = mof.file_content
    atoms_to_remove = []
    for solvent_atoms in mof.solvent_components:
        atoms_to_remove.extend(solvent_atoms)
    file_lines = file_content.split('\n')
    line_index = 0
    while line_index < len(file_lines):
        line = file_lines[line_index]
        if any(line.startswith(atom.label) for atom in atoms_to_remove):
            file_lines.pop(line_index)
        else:
            line_index += 1
    return '\n'.join(file_lines)
