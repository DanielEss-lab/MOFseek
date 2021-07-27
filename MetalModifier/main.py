from MofIdentifier.Molecules.atom import Atom
from MofIdentifier.bondTools import Distances
from MofIdentifier.fileIO import CifReader
from MofIdentifier.subbuilding import SBUIdentifier

import numpy as np
import re
import sys


def replace_metal(input_cif_file_path, output_cif_file_path, new_metal_symbol):
    mof = CifReader.get_mof(input_cif_file_path)
    num_needed = 2  # Todo: get number of protons based on new_metal_symbol
    nodes = SBUIdentifier.split(mof).clusters
    nodes = [node for node in nodes if len(node.atoms) > 1]
    assert (len(nodes) > 0)
    assert (all(node == nodes[0] for node in nodes))
    num_protons = count_added_protons(nodes[0])
    previous_metal_symbol = get_metal_of_node(nodes[0])
    if num_protons > num_needed:
        num_to_delete = num_protons - num_needed
        atoms_to_delete = []
        for node in nodes:
            atoms_to_delete.extend(get_atoms_to_delete(node, num_to_delete))
        file_content = get_file_content_without_atoms(mof.file_content, atoms_to_delete)
    elif num_protons < num_needed:
        num_to_add = num_needed - num_protons
        atoms_to_add = []
        for node in nodes:
            atoms_to_add.extend(get_atoms_to_add(node, num_to_add, mof))
        file_content = get_file_content_with_atoms(mof.file_content, atoms_to_add)
    else:
        file_content = mof.file_content
    # Finally, replace the metal:
    file_lines = file_content.split('\n')
    approximate_main_section = '\n'.join(file_lines[16:])
    approximate_main_section.replace(previous_metal_symbol, new_metal_symbol)
    file_content = '\n'.join(file_lines[0:16]) + '\n' + approximate_main_section

    with open(output_cif_file_path, "w") as f:
        f.write(file_content)


def count_added_protons(node):
    num = 0
    for atom in node.atoms:
        if atom.type_symbol == 'O' and len([neighbor for neighbor in atom.bondedAtoms if neighbor.is_metal()]) > 2:
            for neighbor in atom.bondedAtoms:
                if neighbor.type_symbol == 'H':
                    num += 1
    return num


def get_metal_of_node(node):
    type = ''
    for atom in node.atoms:
        if atom.is_metal():
            if len(type) > 0:
                assert(atom.type_symbol == type)
            type = atom.type_symbol
    return type


def get_atoms_to_delete(node, num_to_delete):
    eligible_atoms = []
    for atom in node.atoms:
        if atom.type_symbol == 'H':
            assert (len(atom.bondedAtoms) == 1)
            oxygen = atom.bondedAtoms[0]
            if oxygen.type_symbol == 'O' and len([neighbor for neighbor in oxygen.bondedAtoms
                                                  if neighbor.is_metal()]) > 2:
                eligible_atoms.append(atom)
    sorted_eligible = list(eligible_atoms)
    sorted_eligible.sort()
    atoms_to_delete = sorted_eligible[0:num_to_delete]
    return atoms_to_delete


def get_atoms_to_add(node, num_to_add, mof):
    eligible_oxygens = []
    for atom in node.atoms:
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
    distance = Distances.distance('O', 'H')
    if len(oxygen.bondedAtoms) == 2:
        O = np.array(oxygen.x, oxygen.y, oxygen.z)
        A = np.array(oxygen.bondedAtoms[0].x, oxygen.bondedAtoms[0].y, oxygen.bondedAtoms[0].z)
        B = np.array(oxygen.bondedAtoms[1].x, oxygen.bondedAtoms[1].y, oxygen.bondedAtoms[1].z)
        midpoint = (B - A)/2 + B
        line = np.norm(O - midpoint)
        H = line * distance
        return Atom.from_cartesian('unlabeled', 'H', H[0], H[1], H[2], mof)
    elif len(oxygen.bondedAtoms) == 3:
        O = np.array(oxygen.x, oxygen.y, oxygen.z)
        A = np.array(oxygen.bondedAtoms[0].x, oxygen.bondedAtoms[0].y, oxygen.bondedAtoms[0].z)
        B = np.array(oxygen.bondedAtoms[1].x, oxygen.bondedAtoms[1].y, oxygen.bondedAtoms[1].z)
        C = np.array(oxygen.bondedAtoms[2].x, oxygen.bondedAtoms[2].y, oxygen.bondedAtoms[2].z)
        u1 = B - A
        c_minus_a = C - A
        w1 = np.matmul(c_minus_a, u1)
        u = np.linalg.norm(u1)
        w = np.linalg.norm(w1)
        v = np.matmul(w, u)
        b = np.array(np.dot(u1, u), 0)
        c = np.array(np.dot(c_minus_a, u), np.dot(c_minus_a, v))
        h = ((c[0]-b[0]/2)**2 + (c[1])**2 - (b[0]/2)**2) / (2*c[1])
        center = A + (b[0]/2) * u + h * v
        line = np.norm(O - center)
        H = line*distance
        return Atom.from_cartesian('unlabeled', 'H', H[0], H[1], H[2], mof)
    else:
        assert False


def get_file_content_without_atoms(file_content, atoms_to_delete):
    file_lines = file_content.split('\n')
    line_index = 0
    while line_index < len(file_lines):
        line = file_lines[line_index]
        if any(line.startswith(atom.label) for atom in atoms_to_delete):
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
