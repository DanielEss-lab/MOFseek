import itertools
import math

import numpy as np

from MofIdentifier.Molecules import MOF
from MofIdentifier.bondTools import Distances

ACCEPTABLE_DISTANCE_ERROR = 0.10
ACCEPTABLE_ANGLE_ERROR = 10


def process(mof: MOF.MOF, verbose=False):
    atoms_with_open_metal_sites = []
    for atom in mof.atoms:
        if not atom.is_metal():
            continue
        if len(atom.bondedAtoms) < 4:
            atoms_with_open_metal_sites.append(atom)
        else:  # 4 or more bonds
            centroid = center_of_bonded_atoms(atom, mof)
            metal_to_center_distance = Distances.distance_across_unit_cells(atom, centroid, mof.angles,
                                                                            mof.fractional_lengths)
            if metal_to_center_distance > ACCEPTABLE_DISTANCE_ERROR:
                atoms_with_open_metal_sites.append(atom)
            elif len(atom.bondedAtoms) == 4:
                # A metal with 4 bonds might have open sites even if the ligands all cancel out spatially
                angles = all_angles_around(atom)
                avg_angle_deviation = sum(abs(angle - 110) for angle in angles) / len(angles)
                if avg_angle_deviation > ACCEPTABLE_ANGLE_ERROR:
                    atoms_with_open_metal_sites.append(atom)  # square planar; open metal sites
                else:
                    pass  # tetrahedral shape; no open metal site
    if verbose and len(atoms_with_open_metal_sites) > 0:
        example_atom = atoms_with_open_metal_sites[0]
        example_num_bonds = len(example_atom.bondedAtoms)
        example_distance = Distances.distance_across_unit_cells(example_atom, center_of_bonded_atoms(example_atom, mof),
                                                                mof.angles, mof.fractional_lengths)
        return atoms_with_open_metal_sites, example_atom, example_num_bonds, example_distance
    else:
        return atoms_with_open_metal_sites


def center_of_bonded_atoms(atom, mof):
    bonded_atoms = [Distances.move_neighbor_if_distant(atom, bonded_atom, mof.angles, mof.fractional_lengths)
                    for bonded_atom in atom.bondedAtoms]
    unit_vectors = [unit_vectorize_bond(atom, bonded_atom) for bonded_atom in bonded_atoms]
    centeroid_x = sum(v[0] for v in unit_vectors)
    centeroid_y = sum(v[1] for v in unit_vectors)
    centeroid_z = sum(v[2] for v in unit_vectors)
    return atom.from_cartesian('Centroid', None, centeroid_x, centeroid_y, centeroid_z, mof)


def unit_vectorize_bond(atom, bonded_atom):
    x_vector = bonded_atom.x - atom.x
    y_vector = bonded_atom.y - atom.y
    z_vector = bonded_atom.z - atom.z
    norm = math.sqrt(x_vector ** 2 + y_vector ** 2 + z_vector ** 2)
    return x_vector/norm, y_vector/norm, z_vector/norm


def all_angles_around(atom):
    angles = []
    for a, b in itertools.combinations(atom.bondedAtoms, 2):
        dist_a = Distances.distance(a, atom)
        dist_b = Distances.distance(b, atom)
        dist_c = Distances.distance(a, b)
        arccos_input = (dist_a ** 2 + dist_b ** 2 - dist_c ** 2) / (2 * dist_a * dist_b)
        if arccos_input > 1 or arccos_input < -1:
            raise Exception("bad arccos input")
        c_angle = np.arccos(arccos_input)
        angles.append(c_angle * 180 / np.pi)
    return angles
