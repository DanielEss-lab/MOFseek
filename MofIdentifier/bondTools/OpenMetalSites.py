import itertools
import math

import numpy as np

from MofIdentifier.bondTools import Distances, CovalentRadiusLookup
from MofIdentifier.fileIO import CifReader

ACCEPTABLE_DISTANCE_ERROR = 0.45  # Increasing distance makes it harder for a metal to qualify as having open sites
ACCEPTABLE_ANGLE_ERROR = 20
TETRAHEDRON_ANGLE = 110


def process(mof, verbose=False):
    atoms_with_open_metal_sites = [atom for atom in mof.atoms if has_open_metal_site(atom, mof)]
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


def has_open_metal_site(atom, mof):
    if not atom.is_metal():
        return False
    if len(atom.bondedAtoms) < 4:
        return True
    else:  # 4 or more bonds
        centroid = center_of_bonded_atoms(atom, mof)
        metal_to_center_distance = Distances.distance_across_unit_cells(atom, centroid, mof.angles,
                                                                        mof.fractional_lengths)
        if metal_to_center_distance > distance_cutoff_for(atom.type_symbol, len(atom.bondedAtoms)):
            return True
        elif len(atom.bondedAtoms) == 4:
            # A metal with 4 bonds might have open sites even if the bonded atom directions all cancel out spatially
            angles = all_angles_around(atom, mof)
            avg_angle_deviation = sum(abs(angle - TETRAHEDRON_ANGLE) for angle in angles) / len(angles)
            if avg_angle_deviation > ACCEPTABLE_ANGLE_ERROR:
                return True  # square planar; open metal sites
            else:
                return False  # tetrahedral shape; no open metal site

def center_of_bonded_atoms(atom, mof):
    bonded_atoms = [Distances.move_neighbor_if_distant(atom, bonded_atom, mof.angles, mof.fractional_lengths)
                    for bonded_atom in collapsed_bonds(atom)]
    unfiltered_unit_vectors = [unit_vectorize_bond(atom, bonded_atom) for bonded_atom in bonded_atoms]
    unit_vectors = [v for v in unfiltered_unit_vectors if v is not None]
    assert (all(0.98 < v[0] ** 2 + v[1] ** 2 + v[2] ** 2 < 1.02 for v in unit_vectors))
    centeroid_relative_x = sum(v[0] for v in unit_vectors)
    centeroid_relative_y = sum(v[1] for v in unit_vectors)
    centeroid_relative_z = sum(v[2] for v in unit_vectors)
    return atom.from_cartesian('Centroid', None, centeroid_relative_x + atom.x,
                               centeroid_relative_y + atom.y,
                               centeroid_relative_z + atom.z, mof)


# For example, the nitrogen ligands on the Tb atoms in LOQSOA_clean
def collapsed_bonds(metal):
    collapsed_bonds = []
    neighbors = metal.bondedAtoms.copy()
    while len(neighbors) > 0:
        neighbor = neighbors.pop()
        if neighbor.type_symbol == 'O':
            if len(neighbor.bondedAtoms) == 2:
                center_of_bonds = [atom for atom in neighbor.bondedAtoms if atom != metal][0]
                neighbors_to_both = [atom for atom in center_of_bonds.bondedAtoms if atom in metal.bondedAtoms and
                             atom.type_symbol == 'O' and len(atom.bondedAtoms) == 2]
                if len(neighbors_to_both) == 2:
                    collapsed_bonds.append(center_of_bonds)
                    continue
        collapsed_bonds.append(neighbor)
    return collapsed_bonds


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


def distance_cutoff_for(type_symbol: str, num_ligands):
    covalent_radius = CovalentRadiusLookup.lookup(type_symbol)
    multiplier = (0.08 * num_ligands) + normalized_radius(covalent_radius)
    return multiplier * ACCEPTABLE_DISTANCE_ERROR


def normalized_radius(covalent_radius):
    return (covalent_radius - CovalentRadiusLookup.smallest_radius())/(CovalentRadiusLookup.greatest_radius() - CovalentRadiusLookup.smallest_radius())


if __name__ == '__main__':
    # mof = CifReader.get_mof(r"C:\Users\mdavid4\Desktop\2019-11-01-ASR-public_12020\structure_10143\ac403674p_si_001_clean.cif")
    # print(mof.sbus().clusters)
    # atoms_with_open_metal_sites, example_atom, example_num_bonds, example_distance = process(mof, True)
    # print(*atoms_with_open_metal_sites)
    # print(example_atom)
    # print(example_num_bonds)
    # print(example_distance)

    print(CovalentRadiusLookup.greatest_radius())
    print(CovalentRadiusLookup.smallest_radius())
    symbol = 'Zr'
    print(f"{symbol}:\tradius {CovalentRadiusLookup.lookup(symbol)},\tnormalized radius "
          f"{normalized_radius(CovalentRadiusLookup.lookup(symbol))},\tcutoff 4 ligands "
          f"{distance_cutoff_for(symbol, 4)},\tcutoff 8 ligands {distance_cutoff_for(symbol, 8)}\n\n---\n")
    # for symbol, radius in CovalentRadiusLookup.data.items():
    #     print(f"{symbol}:\tradius {radius},\tcutoff {distance_cutoff_for(symbol, 6)}")
