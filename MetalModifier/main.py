from MetalModifier import TetrahedronTools
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
        # if atom.type_symbol == 'O' and len([neighbor for neighbor in atom.bondedAtoms if neighbor.is_metal()]) > 2:
        #     for neighbor in atom.bondedAtoms:
        #         if neighbor.type_symbol == 'H':
        #             num += 1
        if atom.type_symbol == 'H':
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

# Hydrogen locations come in 6 groups on M6 nodes:
# 0) The first hydrogens on the oxygens connected to the metals. These would almost never be removed.
# 1) The first 4 mew-3-oxyls
# 2) The second hydrogens on the first oxygen connected to each metal
# 3) The second hydrogens on the second oxygen connected to each metal. Ie you shouldn't have one metal with 2 H2O
#           and another one with 2 OH; rather, both should have 1 H20 and 1 OH
# 4) Each sulfate group can have one of its oxygens connect to a H
# 5) The other 4 mew-3-oxyls
# When adding, add from the top down. When deleting, delete from the bottom up


def get_relevant_group_0_atoms(cluster):
    # 0) The first hydrogens on the oxygens connected to the metals. These would almost never be removed.
    delete_eligible_hydrogens = []
    add_eligible_oxygens = []
    for aux in cluster[1]:
        if any(atom.type_symbol == 'S' or atom.type_symbol == 'P' or atom.type_symbol == 'C' for atom in aux.atoms):
            continue
        oxygen = None
        for atom in aux.atoms:
            if atom.type_symbol == 'O' and oxygen is None:
                oxygen = atom
            elif atom.type_symbol == 'O':
                continue  # Two oxygens, therefore doesn't fit requirements
        hydrogen = None
        for atom in oxygen.bondedAtoms:
            if atom.type_symbol == 'H' and hydrogen is None:
                hydrogen = atom
            elif atom.type_symbol == 'H':
                assert(len([neighbor for neighbor in oxygen.bondedAtoms if neighbor.type_symbol == 'H']) < 2)
        if hydrogen is None:
            add_eligible_oxygens.append(oxygen)
        else:
            delete_eligible_hydrogens.append(hydrogen)
    delete_eligible_hydrogens.sort()
    add_eligible_oxygens.sort()
    return delete_eligible_hydrogens, add_eligible_oxygens


def get_relevant_group_1_atoms(cluster, mof):
    # 1) The first 4 mew-3-oxyls
    delete_eligible_hydrogens = []
    add_eligible_oxygens = []
    for atom in cluster[0].atoms:
        if atom.type_symbol != 'O' or len([neighbor for neighbor in atom.bondedAtoms if neighbor.is_metal()]) != 3:
            continue
        hydrogen = None
        for neighbor in atom.bondedAtoms:
            if neighbor.type_symbol == 'H' and hydrogen is None:
                hydrogen = neighbor
            elif neighbor.type_symbol == 'H':
                assert(len([neighbor for neighbor in atom.bondedAtoms if neighbor.type_symbol == 'H']) < 2)
        if hydrogen is None:
            add_eligible_oxygens.append(atom)
        else:
            delete_eligible_hydrogens.append(hydrogen)
    assert(len(delete_eligible_hydrogens) == 4 or len(delete_eligible_hydrogens) == 0)
    assert(len(add_eligible_oxygens) == 8 or len(add_eligible_oxygens) == 4)
    if add_eligible_oxygens == 8:
        add_eligible_oxygens.sort()
        first_pole = add_eligible_oxygens[0]
        others = [(pole, Distances.distance_across_unit_cells(
            first_pole, pole, mof.angles, mof.lengths)) for pole in add_eligible_oxygens[1:]]
        others.sort(key=lambda pair: pair[1])
        add_eligible_oxygens = [first_pole].extend(others[3:6])  # Not the three closest, neither the one farthest
    delete_eligible_hydrogens.sort()
    add_eligible_oxygens.sort()
    return delete_eligible_hydrogens, add_eligible_oxygens


def get_relevant_groups_2_and_3_atoms(cluster):
    # 2) The second hydrogen atoms on the first oxygen connected to each metal
    # 3) The second hydrogens on the second oxygen connected to each metal. Ie you shouldn't have one metal with 2 H2O
    # and another one with 2 OH; rather, both should have 1 H20 and 1 OH
    h_by_metal = dict()
    o_by_metal = dict()
    for aux in cluster[1]:
        if any(atom.type_symbol == 'S' or atom.type_symbol == 'P' or atom.type_symbol == 'C' for atom in aux.atoms):
            continue
        oxygen = None
        for atom in aux.atoms:
            if atom.type_symbol == 'O' and oxygen is None:
                oxygen = atom
            elif atom.type_symbol == 'O':
                continue  # Two oxygens, therefore doesn't fit requirements
        metal = None
        for atom in oxygen.bondedAtoms:
            if atom.is_metal() and metal is None:
                metal = atom
            elif atom.type_symbol == 'O':
                raise Exception('Oxygen connected to two metal atoms should not be part of an aux group. '
                                'Please contact developer.')
        if metal in o_by_metal:
            o_by_metal[metal].append(oxygen)
        else:
            o_by_metal[metal] = [oxygen]
        hydrogen = []
        for atom in oxygen.bondedAtoms:
            if atom.type_symbol == 'H':
                hydrogen.append(atom)
        if metal in h_by_metal:
            h_by_metal[metal].extend(hydrogen)
        else:
            h_by_metal[metal] = [hydrogen]
    group_2_delete_hydrogens = []
    group_2_add_oxygens = []
    group_3_delete_hydrogens = []
    group_3_add_oxygens = []
    for metal in h_by_metal:
        hydrogens = h_by_metal[metal]
        if len(hydrogens) == 2:
            group_2_add_oxygens.append(o_by_metal[metal][0])
            group_3_add_oxygens.append(o_by_metal[metal][1])
        elif len(hydrogens) == 3:
            if len([neighbor for neighbor in o_by_metal[metal][0].bondedAtoms if neighbor.type_symbol == 'H']) == 2:
                occupied_oxygen = o_by_metal[metal][0]
                other_oxygen = o_by_metal[metal][1]
            else:
                occupied_oxygen = o_by_metal[metal][1]
                other_oxygen = o_by_metal[metal][0]
            group_3_add_oxygens.append(other_oxygen)
            group_2_delete_hydrogens.append([neighbor for neighbor in occupied_oxygen.bondedAtoms if neighbor.type_symbol == 'H'][0])
        elif len(hydrogens) == 4:
            group_3_delete_hydrogens.append([neighbor for neighbor in o_by_metal[metal][0].bondedAtoms if neighbor.type_symbol == 'H'][0])
            group_2_delete_hydrogens.append([neighbor for neighbor in o_by_metal[metal][1].bondedAtoms if neighbor.type_symbol == 'H'][0])
        else:
            raise Exception(f'Error: metal has {len(hydrogens)} protons attached during the group 2/3 phase')
    group_2_delete_hydrogens.sort()
    group_2_add_oxygens.sort()
    group_3_delete_hydrogens.sort()
    group_3_add_oxygens.sort()
    return group_3_delete_hydrogens.extend(group_2_delete_hydrogens), group_2_add_oxygens.extend(group_3_add_oxygens)


def get_relevant_group_4_atoms(cluster):
    # 4) Each sulfate group can have one of its oxygens connect to a H
    delete_eligible_hydrogens = []
    add_eligible_oxygens = []
    for aux in cluster[1]:
        sulfur = None
        for atom in aux:
            if atom.type_symbol == 'S':
                sulfur = atom
        if sulfur is None:
            continue
        eligible_oxygens = []
        for atom in sulfur.bondedAtoms:
            if atom.type_symbol == 'O' and len([neighbor for neighbor in atom.bondedAtoms if neighbor.is_metal()]) == 0:
                eligible_oxygens.append(atom)
        hydrogen = None
        for oxygen in eligible_oxygens:
            for neighbor in oxygen.bondedAtoms:
                if neighbor.type_symbol == 'H':
                    hydrogen = neighbor
        if hydrogen is None:
            add_eligible_oxygens.append(eligible_oxygens[0])
        else:
            delete_eligible_hydrogens.append(hydrogen)
    delete_eligible_hydrogens.sort()
    add_eligible_oxygens.sort()
    return delete_eligible_hydrogens, add_eligible_oxygens


def get_relevant_group_5_atoms(cluster, mof):
    # 1) The other 4 mew-3-oxyls
    delete_eligible_hydrogens = []
    add_eligible_oxygens = []
    for atom in cluster[0].atoms:
        if atom.type_symbol != 'O' or len([neighbor for neighbor in atom.bondedAtoms if neighbor.is_metal()]) != 3:
            continue
        hydrogen = None
        for neighbor in atom.bondedAtoms:
            if neighbor.type_symbol == 'H' and hydrogen is None:
                hydrogen = neighbor
            elif neighbor.type_symbol == 'H':
                assert(len([neighbor for neighbor in atom.bondedAtoms if neighbor.type_symbol == 'H']) < 2)
        if hydrogen is None:
            add_eligible_oxygens.append(atom)
        else:
            delete_eligible_hydrogens.append(hydrogen)
    assert(len(delete_eligible_hydrogens) == 8 or len(delete_eligible_hydrogens) == 4)
    assert(len(add_eligible_oxygens) == 4 or len(add_eligible_oxygens) == 0)
    if delete_eligible_hydrogens == 8:
        delete_eligible_hydrogens.sort()
        first_pole = delete_eligible_hydrogens[7]
        others = [(pole, Distances.distance_across_unit_cells(
            first_pole, pole, mof.angles, mof.lengths)) for pole in delete_eligible_hydrogens[0:7]]
        others.sort(key=lambda pair: pair[1])
        delete_eligible_hydrogens = [first_pole].extend(others[3:6])  # Not the three closest, neither the one farthest
    delete_eligible_hydrogens.sort()
    add_eligible_oxygens.sort()
    return delete_eligible_hydrogens, add_eligible_oxygens


def get_atoms_to_delete(cluster, num_to_delete):
    priority_atoms = []
    for atom in cluster[0].atoms:
        if atom.type_symbol == 'H':
            assert (len(atom.bondedAtoms) == 1)
            oxygen = atom.bondedAtoms[0]
            if oxygen.type_symbol == 'O' and len([neighbor for neighbor in oxygen.bondedAtoms
                                                  if neighbor.is_metal()]) > 2:
                priority_atoms.append(atom)
    priority_atoms.sort()
    if len(priority_atoms) >= num_to_delete:
        atoms_to_delete = priority_atoms[0:num_to_delete]
    else:
        eligible_atoms = []
        second_hydrogens = []
        for aux in cluster[1]:
            if any(atom.type_symbol == 'S' or atom.type_symbol == 'P' for atom in aux.atoms):
                continue
            else:
                num_hydrogens_marked_for_deletion = 0
                for atom in aux.atoms:
                    if atom.type_symbol == 'H':
                        if num_hydrogens_marked_for_deletion == 0:
                            eligible_atoms.append(atom)
                            num_hydrogens_marked_for_deletion += 1
                        elif num_hydrogens_marked_for_deletion == 1:
                            second_hydrogens.append(atom)
                            num_hydrogens_marked_for_deletion += 1
                        else:
                            raise Exception('The developer did not account for aux groups with 3 or more Hydrogens. '
                                            'Please ask him to update the program if you need to use it with such.')
        second_hydrogens.sort()
        eligible_atoms.sort()
        priority_atoms.extend(second_hydrogens)
        priority_atoms.extend(eligible_atoms)
        atoms_to_delete = priority_atoms[0:num_to_delete]
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
    eligible_oxygens.sort()
    for oxygen in eligible_oxygens[0:num_to_add]:
        atoms_to_add.append(make_proton_by(oxygen, mof))
    return atoms_to_add


def make_proton_by(oxygen, mof):
    distance = CovalentRadiusLookup.lookup('O') + CovalentRadiusLookup.lookup('H')
    O = np.array([oxygen.x, oxygen.y, oxygen.z])
    if len(oxygen.bondedAtoms) == 1:
        A = get_close_numpy_vector(oxygen, oxygen.bondedAtoms[0], mof)
        line = normalize(O - A)
        # Rotate the line to make it more accurate when we need to add one here, then add another later.
        R = np.array([[1, 0, 0], [0, 0.87, -0.5], [0, 0.5, 0.87]])
        rotated_line = line * R
        H = O + (rotated_line * distance)
        return Atom.from_cartesian('unlabeled', 'H', H[0], H[1], H[2], mof)
    elif len(oxygen.bondedAtoms) == 2:
        A = get_close_numpy_vector(oxygen, oxygen.bondedAtoms[0], mof)
        B = get_close_numpy_vector(oxygen, oxygen.bondedAtoms[1], mof)
        midpoint = (B + A)/2
        line = normalize(O - midpoint)
        H = O + (line * distance)
        return Atom.from_cartesian('unlabeled', 'H', H[0], H[1], H[2], mof)
    elif len(oxygen.bondedAtoms) == 3:
        A = get_close_numpy_vector(oxygen, oxygen.bondedAtoms[0], mof)
        B = get_close_numpy_vector(oxygen, oxygen.bondedAtoms[1], mof)
        C = get_close_numpy_vector(oxygen, oxygen.bondedAtoms[2], mof)
        possible_points = TetrahedronTools.find_fourth_vertex(A, B, C, 2.85, 2.85, 2.85)
        if np.linalg.norm(O - possible_points[0]) < np.linalg.norm(O - possible_points[1]):
            counterpoint = possible_points[1]
        else:
            counterpoint = possible_points[0]
        line = normalize(O - counterpoint)
        H = O + (line * distance)
        return Atom.from_cartesian('unlabeled', 'H', H[0], H[1], H[2], mof)
    else:
        assert False


def normalize(v):
    norm = np.linalg.norm(v)
    if norm < 0.00001:
        return v
    return v / norm


def get_close_numpy_vector(base_atom, neighbor, mof):
    da = db = dc = 0
    if neighbor.a - base_atom.a > 0.5:
        da -= 1.0
    elif neighbor.a - base_atom.a < -0.5:
        da += 1.0
    if neighbor.b - base_atom.b > 0.5:
        db -= 1.0
    elif neighbor.b - base_atom.b < -0.5:
        db += 1.0
    if neighbor.c - base_atom.c > 0.5:
        dc -= 1.0
    elif neighbor.c - base_atom.c < -0.5:
        dc += 1.0
    neighbor_in_right_place = neighbor.copy_to_relative_position(da, db, dc, mof.angles,
                                                                 mof.fractional_lengths)
    return np.array([neighbor_in_right_place.x, neighbor_in_right_place.y, neighbor_in_right_place.z])


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
            index = int(re.search(r'\d+', line).group(0))
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
