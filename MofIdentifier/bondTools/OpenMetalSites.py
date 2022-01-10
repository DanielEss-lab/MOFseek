import itertools
import math

import numpy as np

from MofIdentifier.Molecules.Atom import Atom
from MofIdentifier.Molecules.Ligand import Ligand
from MofIdentifier.bondTools import Distances, CovalentRadiusLookup, MassLookup
from MofIdentifier.fileIO import CifReader, XyzWriter

ACCEPTABLE_DISTANCE_ERROR = 0.40  # Increasing distance makes it harder for a metal to qualify as having open sites
ACCEPTABLE_ANGLE_ERROR = 20
TETRAHEDRON_ANGLE = 110


def write_estimate(atom, centroids, estimates, name):
    atoms = list()
    atoms.append(atom)
    atoms.extend([Distances.move_neighbor_if_distant(atom, bonded_atom, mof.angles, mof.fractional_lengths)
                  for bonded_atom in atom.bondedAtoms])
    atoms.append(Atom.copy_with_different_type(centroids[0], 'Si'))  # Si is the geometric center
    atoms.append(Atom.copy_with_different_type(centroids[1], 'Sn'))  # Sn is the weight center
    estimate_symbol = 'He' if atom.open_metal_site else 'Xe'
    for estimate in estimates:
        atoms.append(Atom.copy_with_different_type(estimate, estimate_symbol))
    mol = Ligand("temp", atoms, None)
    XyzWriter.write_molecule_to_file(fr"C:\Users\mdavid4\Downloads\{name}.xyz", mol, name)


def write_atom_in_mof(atom_label, mof, name):
    for atom in mof.atoms:
        if atom.label == atom_label:
            centroids = centers_of_bonded_atoms(atom, mof)
            write_estimate(atom, centroids, estimated_bond_sites(atom, centroids, mof), name)


def process(mof, verbose=False):
    atoms_with_open_metal_sites = [atom for atom in mof.atoms if has_open_metal_site(atom, mof)]
    if verbose:
        if len(atoms_with_open_metal_sites) > 0:
            example_atom = atoms_with_open_metal_sites[0]
            example_num_bonds = len(example_atom.bondedAtoms)
            centers = centers_of_bonded_atoms(example_atom, mof)
            example_distances = [Distances.distance_across_unit_cells(example_atom, center, mof.angles,
                                                                     mof.fractional_lengths) for center in centers]
            return atoms_with_open_metal_sites, example_atom, example_num_bonds, max(example_distances)
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
        geom_centroid, mass_centroid = centers_of_bonded_atoms(atom, mof)
        metal_to_center_distances = (Distances.distance_across_unit_cells(atom, geom_centroid, mof.angles,
                                                                          mof.fractional_lengths),
                                     Distances.distance_across_unit_cells(atom, mass_centroid, mof.angles,
                                                                          mof.fractional_lengths))
        cutoff = distance_cutoff_for(atom.type_symbol, len(atom.bondedAtoms))
        if any(d > cutoff for d in metal_to_center_distances):
            return True
        elif len(atom.bondedAtoms) == 4:
            # A metal with 4 bonds might have open sites even if the bonded atom directions all cancel out spatially
            return square_planar_angles(atom, mof)


def square_planar_angles(atom, mof):
    angles = all_angles_around(atom, mof)
    avg_angle_deviation = sum(abs(angle - TETRAHEDRON_ANGLE) for angle in angles) / len(angles)
    if avg_angle_deviation > ACCEPTABLE_ANGLE_ERROR:
        return True  # square planar; open metal sites
    else:
        return False  # tetrahedral shape; no open metal site


def centers_of_bonded_atoms(atom, mof):
    #
    bonded_atoms = [Distances.move_neighbor_if_distant(atom, bonded_atom, mof.angles, mof.fractional_lengths)
                    for bonded_atom in atom.bondedAtoms]
    unfiltered_unit_vectors = [unit_vectorize_bond(atom, bonded_atom) for bonded_atom in bonded_atoms]
    unit_vectors = [v for v in unfiltered_unit_vectors if v is not None]
    assert (all(0.98 < v[0] ** 2 + v[1] ** 2 + v[2] ** 2 < 1.02 for v in unit_vectors))
    centeroid_relative_x = sum(v[0] for v in unit_vectors)
    centeroid_relative_y = sum(v[1] for v in unit_vectors)
    centeroid_relative_z = sum(v[2] for v in unit_vectors)
    geometric_center = atom.from_cartesian('Centroid', None, centeroid_relative_x + atom.x,
                                           centeroid_relative_y + atom.y,
                                           centeroid_relative_z + atom.z, mof)

    average_weight = sum(MassLookup.lookup(bonded_atom.type_symbol) for bonded_atom in bonded_atoms) / len(bonded_atoms)
    unfiltered_mass_vectors = [mass_vectorize_bond(atom, bonded_atom, average_weight) for bonded_atom in bonded_atoms]
    mass_vectors = [v for v in unfiltered_mass_vectors if v is not None]
    centeroid_relative_x = sum(v[0] for v in mass_vectors)
    centeroid_relative_y = sum(v[1] for v in mass_vectors)
    centeroid_relative_z = sum(v[2] for v in mass_vectors)
    mass_center = atom.from_cartesian('Centroid', None, centeroid_relative_x + atom.x,
                                      centeroid_relative_y + atom.y,
                                      centeroid_relative_z + atom.z, mof)
    # # test code
    # unfiltered_mass_vectors = [mass_vectorize_bond(atom, bonded_atom) for bonded_atom in bonded_atoms]
    # mass_vectors = [v for v in unfiltered_mass_vectors if v is not None]
    # centeroid_relative_x = sum(v[0] for v in mass_vectors)
    # centeroid_relative_y = sum(v[1] for v in mass_vectors)
    # centeroid_relative_z = sum(v[2] for v in mass_vectors)
    # geometric_center = atom.from_cartesian('Centroid', None, centeroid_relative_x + atom.x,
    #                                   centeroid_relative_y + atom.y,
    #                                   centeroid_relative_z + atom.z, mof)
    # # end test code
    return geometric_center, mass_center


def estimated_bond_site(atom, centroid, mof):
    centroid_opposite_dx = atom.x - centroid.x
    centroid_opposite_dy = atom.y - centroid.y
    centroid_opposite_dz = atom.z - centroid.z
    # length = twice the covalent radius of the atom
    estimated_distance = CovalentRadiusLookup.lookup(atom.type_symbol) * 1.5
    metal_to_center_distance = Distances.distance_across_unit_cells(atom, centroid, mof.angles, mof.fractional_lengths)
    if metal_to_center_distance < 0.05 and len(atom.bondedAtoms) < 4:
        return
    estimated_x = atom.x + centroid_opposite_dx / metal_to_center_distance * estimated_distance
    estimated_y = atom.y + centroid_opposite_dy / metal_to_center_distance * estimated_distance
    estimated_z = atom.z + centroid_opposite_dz / metal_to_center_distance * estimated_distance
    estimate = Atom.from_cartesian('Estimate', None, estimated_x, estimated_y, estimated_z, mof)
    return estimate

def estimated_bond_sites(atom, centroids, mof):
    estimates = []
    for centroid in centroids:
        estimate = estimated_bond_site(atom, centroid, mof)
        estimates.append(estimate)
    return estimates


def unit_vectorize_bond(atom, bonded_atom):
    x_vector = bonded_atom.x - atom.x
    y_vector = bonded_atom.y - atom.y
    z_vector = bonded_atom.z - atom.z
    if abs(x_vector) + abs(y_vector) + abs(z_vector) < 0.001:
        # The two atoms have the same location (malformed MOF)
        return None
    norm = math.sqrt(x_vector ** 2 + y_vector ** 2 + z_vector ** 2)
    return x_vector / norm, y_vector / norm, z_vector / norm


def mass_vectorize_bond(atom, bonded_atom, average_weight):
    x_vector = bonded_atom.x - atom.x
    y_vector = bonded_atom.y - atom.y
    z_vector = bonded_atom.z - atom.z
    if abs(x_vector) + abs(y_vector) + abs(z_vector) < 0.001:
        # The two atoms have the same location (malformed MOF)
        return None
    norm = math.sqrt(x_vector ** 2 + y_vector ** 2 + z_vector ** 2)
    this_weight = MassLookup.lookup(bonded_atom.type_symbol)
    x = x_vector / norm * this_weight / average_weight
    y = y_vector / norm * this_weight / average_weight
    z = z_vector / norm * this_weight / average_weight
    return x, y, z


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
    return (covalent_radius - CovalentRadiusLookup.smallest_radius()) / (
            CovalentRadiusLookup.greatest_radius() - CovalentRadiusLookup.smallest_radius())


if __name__ == '__main__':
    # for name, metal in {'LOQSOA_clean': 'Tb1',
    #                     'AGUTUS_clean': 'Cu1',
    #                     'ABAYIO_clean': 'Mn31',
    #                     'AFITUF_clean': 'Zn11',
    #                     'ac403674p_si_001_clean': 'Zn1',
    #                     'acs.inorgchem.6b00894_ic6b00894_si_003_clean': 'Cd11',
    #                     'ACAKUM_clean': 'La3',
    #                     'mofs_30-pos-final-O': 'Zr123',
    #                     'cg501012e_si_002_clean': 'Zn4',
    #                     'DANZAV_charged': 'Cd13',
    #                     'ELIYUU_clean': 'Zn7',
    #                     'FAZPED_clean': 'Co2',
    for name, metal in {'RANPAA_clean': 'La1'}.items():
        mof = CifReader.get_mof(
            fr"C:\Users\mdavid4\Desktop\2019-11-01-ASR-public_12020\structure_10143\{name}.cif")
        write_atom_in_mof(metal, mof, f'{name}_{metal}_OMS_calculation')
    # print(mof.sbus().clusters)
    # atoms_with_open_metal_sites, example_atom, example_num_bonds, example_distance = process(mof, True)
    # print(*atoms_with_open_metal_sites)
    # print(example_atom)
    # print(example_num_bonds)
    # print(example_distance)

    # mof = CifReader.get_mof(
    #     r"C:\Users\mdavid4\Desktop\2019-11-01-ASR-public_12020\structure_10143\AQOLID_clean.cif")
    # for atom in mof.atoms:
    #     if len(atom.bondedAtoms) == 0:
    #         print(atom.label)

    # print(CovalentRadiusLookup.greatest_radius())
    # print(CovalentRadiusLookup.smallest_radius())
    # symbol = 'Zr'
    # print(f"{symbol}:\tradius {CovalentRadiusLookup.lookup(symbol)},\tnormalized radius "
    #       f"{normalized_radius(CovalentRadiusLookup.lookup(symbol))},\tcutoff 4 ligands "
    #       f"{distance_cutoff_for(symbol, 4)},\tcutoff 8 ligands {distance_cutoff_for(symbol, 8)}\n\n---\n")
    # for symbol, radius in CovalentRadiusLookup.data.items():
    #     print(f"{symbol}:\tradius {radius},\tcutoff {distance_cutoff_for(symbol, 6)}")
