import itertools
import math

import numpy as np

from MofIdentifier.Molecules import MOF
from MofIdentifier.bondTools import Distances, CovalentRadiusLookup
from MofIdentifier.fileIO import CifReader

ACCEPTABLE_DISTANCE_ERROR = 0.55  # Increasing distance makes it harder for a metal to qualify as having open sites
ACCEPTABLE_ANGLE_ERROR = 20
TETRAHEDRON_ANGLE = 110


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
            if metal_to_center_distance > distance_cutoff_for(atom.type_symbol):
                atoms_with_open_metal_sites.append(atom)
            elif len(atom.bondedAtoms) == 4:
                # A metal with 4 bonds might have open sites even if the ligands all cancel out spatially
                angles = all_angles_around(atom, mof)
                avg_angle_deviation = sum(abs(angle - TETRAHEDRON_ANGLE) for angle in angles) / len(angles)
                if avg_angle_deviation > ACCEPTABLE_ANGLE_ERROR:
                    atoms_with_open_metal_sites.append(atom)  # square planar; open metal sites
                else:
                    pass  # tetrahedral shape; no open metal site
    if verbose:
        if len(atoms_with_open_metal_sites) > 0:
            example_atom = atoms_with_open_metal_sites[0]
            example_num_bonds = len(example_atom.bondedAtoms)
            example_distance = Distances.distance_across_unit_cells(example_atom,
                                                                    center_of_bonded_atoms(example_atom, mof),
                                                                    mof.angles, mof.fractional_lengths)
            return atoms_with_open_metal_sites, example_atom, example_num_bonds, example_distance
        else:
            return [], None, None, None
    else:
        return atoms_with_open_metal_sites


def center_of_bonded_atoms(atom, mof):
    bonded_atoms = [Distances.move_neighbor_if_distant(atom, bonded_atom, mof.angles, mof.fractional_lengths)
                    for bonded_atom in atom.bondedAtoms]
    unfiltered_unit_vectors = [unit_vectorize_bond(atom, bonded_atom) for bonded_atom in bonded_atoms]
    unit_vectors = [v for v in unfiltered_unit_vectors if v is not None]
    assert (all(0.98 < v[0] ** 2 + v[1] ** 2 + v[2] ** 2 < 1.02 for v in unit_vectors))
    centeroid_relative_x = sum(v[0] for v in unit_vectors)
    centeroid_relative_y = sum(v[1] for v in unit_vectors)
    centeroid_relative_z = sum(v[2] for v in unit_vectors)
    return atom.from_cartesian('Centroid', None, centeroid_relative_x + atom.x,
                               centeroid_relative_y + atom.y,
                               centeroid_relative_z + atom.z, mof)


def unit_vectorize_bond(atom, bonded_atom):
    x_vector = bonded_atom.x - atom.x
    y_vector = bonded_atom.y - atom.y
    z_vector = bonded_atom.z - atom.z
    if abs(x_vector) + abs(y_vector) + abs(z_vector) < 0.001:
        # The two atoms have the same location (malformed MOF)
        return None
    norm = math.sqrt(x_vector ** 2 + y_vector ** 2 + z_vector ** 2)
    return x_vector / norm, y_vector / norm, z_vector / norm


def all_angles_around(atom, mof):
    angles = []
    for a, b in itertools.combinations(atom.bondedAtoms, 2):
        dist_a = Distances.distance_across_unit_cells(a, atom, mof.angles, mof.fractional_lengths)
        dist_b = Distances.distance_across_unit_cells(b, atom, mof.angles, mof.fractional_lengths)
        dist_c = Distances.distance_across_unit_cells(a, b, mof.angles, mof.fractional_lengths)
        # Sometimes the distance values just barely don't make a triangle. This happens if a and b are 180 degrees apart
        # or 0 degrees apart. The following if statement checks for these extremes, and changes the input to the arccos
        # function so that it will produce the correct angle.
        if -0.01 < dist_a - (dist_b + dist_c) < 0.01:
            arccos_input = -1 if dist_c > 0.01 else 1
        elif -0.01 < dist_b - (dist_a + dist_c) < 0.01:
            arccos_input = -1 if dist_c > 0.01 else 1
        elif -0.01 < dist_c - (dist_b + dist_a) < 0.01:
            arccos_input = -1 if dist_c > 0.01 else 1
        else:
            arccos_input = (dist_a ** 2 + dist_b ** 2 - dist_c ** 2) / (2 * dist_a * dist_b)
        if arccos_input > 1 or arccos_input < -1:
            print(mof.label)
            raise Exception("bad arccos input")
        c_angle = np.arccos(arccos_input)
        angles.append(c_angle * 180 / np.pi)
    return angles


def distance_cutoff_for(type_symbol: str):
    covalent_radius = CovalentRadiusLookup.lookup(type_symbol)
    normalized_radius = (covalent_radius - CovalentRadiusLookup.smallest_radius()) \
                        / (CovalentRadiusLookup.greatest_radius() - CovalentRadiusLookup.smallest_radius())
    multiplier = 0.1 + normalized_radius
    return multiplier * ACCEPTABLE_DISTANCE_ERROR


if __name__ == '__main__':
    # mof = CifReader.get_mof(r"C:\Users\mdavid4\Desktop\2019-11-01-ASR-public_12020\structure_10143\ABAYIO_clean.cif")
    # print(mof.sbus().clusters)
    # atoms_with_open_metal_sites, example_atom, example_num_bonds, example_distance = process(mof, True)
    # print(*atoms_with_open_metal_sites)
    # print(example_atom)
    # print(example_num_bonds)
    # print(example_distance)
    print(CovalentRadiusLookup.greatest_radius())
    print(CovalentRadiusLookup.smallest_radius())
    for symbol, radius in CovalentRadiusLookup.data.items():
        print(f"{symbol}:\tradius {radius},\tcutoff {distance_cutoff_for(symbol)}")
