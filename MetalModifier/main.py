from MofIdentifier.Molecules.atom import Atom
from MofIdentifier.bondTools import Distances, CovalentRadiusLookup
from MofIdentifier.fileIO import CifReader
from MofIdentifier.subbuilding import SBUIdentifier

import numpy as np
import re
import sys


def replace_metal(input_cif_file_path, output_cif_file_path, new_metal_symbol):
    mof = CifReader.get_mof(input_cif_file_path)
    num_needed = protons_needed(new_metal_symbol)
    clusters = SBUIdentifier.split(mof, True).nodes_with_auxiliaries().items()
    clusters = [cluster for cluster in clusters if len(cluster[0].atoms) > 1]
    assert (len(clusters) > 0)
    assert (all(cluster[0] == clusters[0][0] for cluster in clusters))
    num_protons = count_added_protons(clusters[0])
    previous_metal_symbol = get_metal_of_node(clusters[0][0])
    if num_protons > num_needed:
        num_to_delete = num_protons - num_needed
        atoms_to_delete = []
        for cluster in clusters:
            atoms_to_delete.extend(get_atoms_to_delete(cluster, num_to_delete))
        file_content = get_file_content_without_atoms(mof.file_content, atoms_to_delete)
    elif num_protons < num_needed:
        num_to_add = num_needed - num_protons
        atoms_to_add = []
        for cluster in clusters:
            atoms_to_add.extend(get_atoms_to_add(cluster, num_to_add, mof))
        file_content = get_file_content_with_atoms(mof.file_content, atoms_to_add)
    else:
        file_content = mof.file_content
    # Finally, replace the metal:
    file_lines = file_content.split('\n')
    approximate_main_section = '\n'.join(file_lines[16:])
    approximate_main_section = approximate_main_section.replace(previous_metal_symbol, new_metal_symbol)
    file_content = '\n'.join(file_lines[0:16]) + '\n' + approximate_main_section

    with open(output_cif_file_path, "w") as f:
        f.write(file_content)


def protons_needed(new_metal_symbol):
    if new_metal_symbol in ['Sc', 'Y', 'La', 'Ac']:
        return 24
    elif new_metal_symbol in ['Ti', 'Zr', 'Hf', 'Rf']:
        return 18
    elif new_metal_symbol in ['V', 'Nb', 'Ta', 'Db']:
        return 12
    else:
        assert new_metal_symbol in ['Sc', 'Y', 'La', 'Ac', 'Ti', 'Zr', 'Hf', 'Rf', 'V', 'Nb', 'Ta', 'Db']
        return None


def count_added_protons(cluster):
    node = cluster[0]
    auxiliaries = cluster[1]
    num = 0
    for atom in node.atoms:
        if atom.type_symbol == 'O' and len([neighbor for neighbor in atom.bondedAtoms if neighbor.is_metal()]) > 2:
            for neighbor in atom.bondedAtoms:
                if neighbor.type_symbol == 'H':
                    num += 1
    for aux in auxiliaries:
        for atom in aux.atoms:
            if atom.type_symbol == 'H':
                num += 1
    return num


def get_metal_of_node(node):
    type_s = ''
    for atom in node.atoms:
        if atom.is_metal():
            if len(type_s) > 0:
                assert(atom.type_symbol == type_s)
            type_s = atom.type_symbol
    return type_s


def get_atoms_to_delete(cluster, num_to_delete):
    priority_atoms = []
    for atom in cluster[0].atoms:
        if atom.type_symbol == 'H':
            assert (len(atom.bondedAtoms) == 1)
            oxygen = atom.bondedAtoms[0]
            if oxygen.type_symbol == 'O' and len([neighbor for neighbor in oxygen.bondedAtoms
                                                  if neighbor.is_metal()]) > 2:
                priority_atoms.append(atom)
    sorted_priority = list(priority_atoms)
    sorted_priority.sort()
    if len(sorted_priority) >= num_to_delete:
        atoms_to_delete = sorted_priority[0:num_to_delete]
    else:
        eligible_atoms = []
        for aux in cluster[1]:
            if any(atom.type_symbol == 'S' or atom.type_symbol == 'P' for atom in aux.atoms):
                continue
            else:
                for atom in aux.atoms:
                    if atom.type_symbol == 'H':
                        eligible_atoms.append(atom)
        sorted_eligible = list(eligible_atoms)
        sorted_eligible.sort()
        sorted_priority.extend(sorted_eligible)
        atoms_to_delete = sorted_priority[0:num_to_delete]
    assert(len(atoms_to_delete) == num_to_delete)
    return atoms_to_delete


def get_atoms_to_add(cluster, num_to_add, mof):
    doubly_empty_oxygens = []
    priority_oxygens = []
    for aux in cluster[1]:
        if any(atom.type_symbol == 'S' or atom.type_symbol == 'P' for atom in aux.atoms)\
                or len([atom for atom in aux.atoms if atom.type_symbol == 'O']) != 1:
            continue
        else:
            for atom in aux.atoms:
                if atom.type_symbol == 'O' and len(atom.bondedAtoms) < 3:
                    if len(atom.bondedAtoms) < 2:
                        doubly_empty_oxygens.append(atom)
                    else:
                        priority_oxygens.append(atom)
    doubly_empty_oxygens.sort()
    priority_oxygens.sort()
    atoms_to_add = []
    # First, put one H on each O that has space for 2
    oxygen_index = 0
    while num_to_add > 0 and oxygen_index < len(doubly_empty_oxygens):
        num_to_add -= 1
        atoms_to_add.append(make_proton_by(doubly_empty_oxygens[oxygen_index], mof))
        oxygen_index += 1
    # Then, put one H on each other O that has space for 1
    oxygen_index = 0
    while num_to_add > 0 and oxygen_index < len(priority_oxygens):
        num_to_add -= 1
        atoms_to_add.append(make_proton_by(priority_oxygens[oxygen_index], mof))
        oxygen_index += 1
    # Then, revisit the first ones and fill their second spaces
    oxygen_index = 0
    while num_to_add > 0 and oxygen_index < len(doubly_empty_oxygens):
        num_to_add -= 1
        atoms_to_add.append(make_proton_by(doubly_empty_oxygens[oxygen_index], mof))
        oxygen_index += 1
    # Finally, start to fill (overfill?) the oxygens that are part of the core node.
    eligible_oxygens = []
    for atom in cluster[0].atoms:
        if atom.type_symbol == 'O' and len([neighbor for neighbor in atom.bondedAtoms if neighbor.is_metal()]) > 2 \
                and len([neighbor for neighbor in atom.bondedAtoms if neighbor.type_symbol == 'H']) == 0:
            eligible_oxygens.append(atom)
    sorted_eligible = list(eligible_oxygens)
    sorted_eligible.sort()
    atoms_to_add = []
    for oxygen in sorted_eligible[0:num_to_add]:
        atoms_to_add.append(make_proton_by(oxygen, mof))
    return atoms_to_add


def make_proton_by(oxygen, mof):
    distance = CovalentRadiusLookup.lookup('O') + CovalentRadiusLookup.lookup('H')
    if len(oxygen.bondedAtoms) == 1:
        O = np.array([oxygen.x, oxygen.y, oxygen.z])
        A = np.array([oxygen.bondedAtoms[0].x, oxygen.bondedAtoms[0].y, oxygen.bondedAtoms[0].z])
        line = normalize(O - A)
        # Rotate the line to make it more accurate when we need to add one here, then add another later.
        R = np.array([[1, 0, 0], [0, 0.87, -0.5], [0, 0.5, 0.87]])
        rotated_line = np.matmul(line, R)
        H = O + (rotated_line * distance)
        return Atom.from_cartesian('unlabeled', 'H', H[0], H[1], H[2], mof)
    elif len(oxygen.bondedAtoms) == 2:
        O = np.array([oxygen.x, oxygen.y, oxygen.z])
        A = np.array([oxygen.bondedAtoms[0].x, oxygen.bondedAtoms[0].y, oxygen.bondedAtoms[0].z])
        B = np.array([oxygen.bondedAtoms[1].x, oxygen.bondedAtoms[1].y, oxygen.bondedAtoms[1].z])
        midpoint = (B - A)/2 + B
        line = normalize(O - midpoint)
        H = O + (line * distance)
        return Atom.from_cartesian('unlabeled', 'H', H[0], H[1], H[2], mof)
    elif len(oxygen.bondedAtoms) == 3:
        O = np.array([oxygen.x, oxygen.y, oxygen.z])
        A = np.array([oxygen.bondedAtoms[0].x, oxygen.bondedAtoms[0].y, oxygen.bondedAtoms[0].z])
        B = np.array([oxygen.bondedAtoms[1].x, oxygen.bondedAtoms[1].y, oxygen.bondedAtoms[1].z])
        C = np.array([oxygen.bondedAtoms[2].x, oxygen.bondedAtoms[2].y, oxygen.bondedAtoms[2].z])
        u1 = B - A
        c_minus_a = C - A
        w1 = np.matmul(c_minus_a, u1)  #TODO: why is this not a vector?
        u = normalize(u1)
        w = normalize(w1)
        v = np.matmul(w, u)
        b = np.array([np.dot(u1, u), 0])
        c = np.array([np.dot(c_minus_a, u), np.dot(c_minus_a, v)])
        h = ((c[0]-b[0]/2)**2 + (c[1])**2 - (b[0]/2)**2) / (2*c[1])
        center = A + (b[0]/2) * u + h * v
        line = normalize(O - center)
        H = O + (line * distance)
        return Atom.from_cartesian('unlabeled', 'H', H[0], H[1], H[2], mof)
    else:
        assert False


def normalize(v):
    norm = np.linalg.norm(v)
    if norm < 0.00001:
        return v
    return v / norm


def get_file_content_without_atoms(file_content, atoms_to_delete):
    file_lines = file_content.split('\n')
    line_index = 0
    while line_index < len(file_lines):
        line = file_lines[line_index]
        if any(line.startswith(atom.label + ' ') for atom in atoms_to_delete):
            file_lines.pop(line_index)
        else:
            line_index += 1
    return '\n'.join(file_lines)


def get_file_content_with_atoms(file_content, atoms_to_add):
    file_lines = file_content.split('\n')
    greatest_existing_H_index = -1
    for line in file_lines:
        if line.startswith('H') and line[1].isdigit():
            index = re.search(r'\d+', line).group(0)
            greatest_existing_H_index = max(greatest_existing_H_index, index)
    for atom in atoms_to_add:
        greatest_existing_H_index += 1
        label = atom.type_symbol + str(greatest_existing_H_index)
        file_lines.append(atom_to_line(label, atom))
    return '\n'.join(file_lines)


def atom_to_line(label, atom):
    return f'{label}   {atom.type_symbol}   {atom.a}   {atom.b}   {atom.c}   {1.0000}'


if __name__ == '__main__':
    if len(sys.argv) == 4:
        replace_metal(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print('Incorrect calling of main method.\nUsage: python main input_cif_file_path output_cif_file_path '
              'new_metal_symbol')
