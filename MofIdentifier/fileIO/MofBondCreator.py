import itertools
from math import floor

import numpy as np

from MofIdentifier.bondTools import Distances, OpenMetalSites, CovalentRadiusLookup, Angles
from collections import namedtuple
from MofIdentifier.Molecules.Atom import Atom

max_bond_length = 4.1
# max_bond_length 5.2 is a worst-case scenario that probably won't occur in most real mofs;
# a more realistic (and still cautious) value would be ~3.5


class MofBondCreator:
    def __init__(self, atoms, angles, fractional_lengths, cartesian_lengths, volume):
        self.angles = angles
        self.lengths = fractional_lengths
        self.atoms: list[Atom] = atoms
        self.volume = volume
        # Floor the number of buckets to overestimate the size of buckets
        # to ensure we're comparing at all viable distances
        self.num_x_buckets = floor(cartesian_lengths[0] / max_bond_length) if cartesian_lengths[0] > max_bond_length else 1
        self.num_y_buckets = floor(cartesian_lengths[1] / max_bond_length) if cartesian_lengths[1] > max_bond_length else 1
        self.num_z_buckets = floor(cartesian_lengths[2] / max_bond_length) if cartesian_lengths[2] > max_bond_length else 1
        self.cellSpace = [[[list(()) for _ in range(self.num_x_buckets)] for _ in range(self.num_y_buckets)]
                          for _ in range(self.num_z_buckets)]
        # To calculate accurate distances, and therefore to calculate the number of partitions in the 3D space,
        # we needed to use cartesian coordinates (usually x, y, and z)
        # However, to assign atoms to buckets, and to copy buckets over to simulate atoms outside the unit cell,
        # the math remains simpler to use fractional coordinates (usually a, b, and c). Unfortunately, we refer to the
        # index of buckets by x y and z instead of a b and c
        for atom in self.atoms:
            x_bucket = floor(atom.a * self.num_x_buckets)
            y_bucket = floor(atom.b * self.num_y_buckets)
            z_bucket = floor(atom.c * self.num_z_buckets)
            self.cellSpace[z_bucket][y_bucket][x_bucket].append(atom)
        self.error_margin = Distances.bond_length_multiplicative_error_margin

    def get_bucket(self, z, y, x) -> list:
        bucket_belongs_to_unit_cell = True
        da, db, dc = 0, 0, 0
        if 0 <= z < self.num_z_buckets:
            plane = self.cellSpace[z]
        else:
            bucket_belongs_to_unit_cell = False
            plane = self.cellSpace[z % self.num_z_buckets]
            dc = 1 if z > 0 else -1
        if 0 <= y < self.num_y_buckets:
            row = plane[y]
        else:
            bucket_belongs_to_unit_cell = False
            row = plane[y % self.num_y_buckets]
            db = 1 if y > 0 else -1
        if 0 <= x < self.num_x_buckets:
            bucket = row[x]
        else:
            bucket_belongs_to_unit_cell = False
            bucket = row[x % self.num_x_buckets]
            da = 1 if x > 0 else -1

        if bucket_belongs_to_unit_cell:
            return bucket
        else:
            bucket_copy = list(())
            for atom in bucket:
                bucket_copy.append(atom.copy_to_relative_position(da, db, dc, self.angles, self.lengths))
            return bucket_copy

    def connect_atoms(self):
        if self.error_margin != Distances.bond_length_multiplicative_error_margin:
            self.reset()
        for z in range(self.num_z_buckets):
            for y in range(self.num_y_buckets):
                for x in range(self.num_x_buckets):
                    this_space = self.cellSpace[z][y][x]
                    spaces_to_compare = self.get_spaces_adj_in_one_direction(x, y, z)
                    self.connect_within_space(this_space)
                    self.connect_within_spaces(this_space, spaces_to_compare)
        self.enforce_single_hydrogen_bonds()
        open_metal_sites = self.fill_nearly_closed_metal_sites()
        self.undo_bad_metal_bonds()
        return open_metal_sites

    def get_spaces_adj_in_one_direction(self, x, y, z):
        # in 2D space, you only need to compare each square with 4 other squares in order for each square
        # to be compared with all 8 adjacent (including diagonals) neighbors. For example, if you compare
        # each square with the square to its right, you don't also need to compare each square with the square to
        # its left. The following code makes use of that principle except in 3Dspace. These 13, their opposites,
        # and the cube itself comprise the entire 3x3x3 region. This way, no comparison happens twice.
        near_space = self.get_bucket(z, y, x+1) \
                     + self.get_bucket(z, y+1, x) \
                     + self.get_bucket(z+1, y, x) \
                     + self.get_bucket(z, y+1, x+1) \
                     + self.get_bucket(z+1, y, x+1) \
                     + self.get_bucket(z+1, y+1, x) \
                     + self.get_bucket(z+1, y+1, x+1) \
                     + self.get_bucket(z-1, y, x+1) \
                     + self.get_bucket(z-1, y+1, x+1) \
                     + self.get_bucket(z-1, y+1, x) \
                     + self.get_bucket(z, y+1, x-1) \
                     + self.get_bucket(z+1, y-1, x+1) \
                     + self.get_bucket(z+1, y+1, x-1)
        return near_space

    def get_all_nearby_space(self, x, y, z):
        near_space = self.get_bucket(z, y, x) \
                     + self.get_bucket(z,   y,   x+1) + self.get_bucket(z,   y,   x-1) \
                     + self.get_bucket(z,   y+1, x)   + self.get_bucket(z,   y-1, x)   \
                     + self.get_bucket(z+1, y,   x)   + self.get_bucket(z-1, y,   x)   \
                     + self.get_bucket(z,   y+1, x+1) + self.get_bucket(z,   y-1, x-1) \
                     + self.get_bucket(z+1, y,   x+1) + self.get_bucket(z-1, y,   x-1) \
                     + self.get_bucket(z+1, y+1, x)   + self.get_bucket(z-1, y-1, x)   \
                     + self.get_bucket(z+1, y+1, x+1) + self.get_bucket(z-1, y-1, x-1) \
                     + self.get_bucket(z-1, y,   x+1) + self.get_bucket(z+1, y,   x-1) \
                     + self.get_bucket(z-1, y+1, x+1) + self.get_bucket(z+1, y-1, x-1) \
                     + self.get_bucket(z-1, y+1, x)   + self.get_bucket(z+1, y-1, x)   \
                     + self.get_bucket(z,   y+1, x-1) + self.get_bucket(z,   y-1, x+1) \
                     + self.get_bucket(z+1, y-1, x+1) + self.get_bucket(z-1, y+1, x-1) \
                     + self.get_bucket(z+1, y+1, x-1) + self.get_bucket(z-1, y-1, x+1)
        return near_space

    def connect_within_space(self, space):
        for i in range(len(space)):
            for j in range(i+1, len(space)):
                self.compare_for_bond(space[i], space[j])

    def connect_within_spaces(self, space_a, space_b):
        for atom_a in space_a:
            for atom_b in space_b:
                self.compare_for_bond(atom_a, atom_b)

    def compare_for_bond(self, atom_a, atom_b):
        dist = Distances.distance(atom_a, atom_b)
        if Distances.is_bond_distance(dist, atom_a, atom_b, self.error_margin):
            if not atom_a.is_in_unit_cell() or not atom_b.is_in_unit_cell():
                if not atom_a.is_in_unit_cell() and not atom_b.is_in_unit_cell():
                    raise Exception
            atom_a.bondedAtoms.append(atom_b)
            atom_b.bondedAtoms.append(atom_a)

    def enforce_single_hydrogen_bonds(self):
        for atom in self.atoms:
            if atom.type_symbol == 'H' and len(atom.bondedAtoms) > 1:
                self.remove_distant_bonds(atom)

    def remove_distant_bonds(self, atom):
        lowest_distance = float('inf')
        closest_atom = None
        for neighbor in atom.bondedAtoms:
            distance = Distances.distance_across_unit_cells(atom, neighbor, self.angles, self.lengths)
            if distance < lowest_distance:
                lowest_distance = distance
                closest_atom = neighbor
        for neighbor in atom.bondedAtoms.copy():
            if neighbor != closest_atom:
                neighbor.bondedAtoms.remove(atom)
                atom.bondedAtoms.remove(neighbor)

    def reset(self):
        for atom in self.atoms:
            atom.bondedAtoms = []

    # Sometimes a particular bond is larger than I can stretch my algorithms to allow, but is clearly there. The main
    # indicator of this is assymetry in a metal's bonds, where it may see that there is an open metal site but really
    # there's simply an atom that the metal is bonding but the algorithm didn't catch.
    def fill_nearly_closed_metal_sites(self):
        open_metal_sites = list()
        Moflike = namedtuple('Moflike', 'fractional_lengths angles unit_volume')
        mof = Moflike(self.lengths, self.angles, self.volume)
        open_site_metals = (atom for atom in self.atoms if OpenMetalSites.has_open_metal_site(atom, mof))
        for atom in open_site_metals:
            centroid = OpenMetalSites.center_of_bonded_atoms(atom, mof)
            metal_to_center_distance = Distances.distance_across_unit_cells(atom, centroid, self.angles, self.lengths)
            if len(atom.bondedAtoms) == 4 and metal_to_center_distance < 0.1:
                self.attempt_to_fill_antiplanar_sites(atom, mof)
            else:
                self.attempt_to_fill_countercenter_site(atom, centroid, metal_to_center_distance, mof)
            if atom.open_metal_site:
                open_metal_sites.append(atom)
        return open_metal_sites

    def attempt_to_fill_countercenter_site(self, atom, centroid, metal_to_center_distance, mof):
        centroid_opposite_dx = atom.x - centroid.x
        centroid_opposite_dy = atom.y - centroid.y
        centroid_opposite_dz = atom.z - centroid.z
        # length = twice the covalent radius of the atom
        estimated_distance = CovalentRadiusLookup.lookup(atom.type_symbol) * 1.5
        if metal_to_center_distance < 0.05 and len(atom.bondedAtoms) < 4:
            return
        estimated_x = atom.x + centroid_opposite_dx / metal_to_center_distance * estimated_distance
        estimated_y = atom.y + centroid_opposite_dy / metal_to_center_distance * estimated_distance
        estimated_z = atom.z + centroid_opposite_dz / metal_to_center_distance * estimated_distance
        estimate = Atom.from_cartesian('Estimate', None, estimated_x, estimated_y, estimated_z, mof)
        filling_atom = self.atom_near(estimate, estimated_distance / 4, atom)
        if filling_atom is None:
            atom.open_metal_site = True
        else:
            atom.bondedAtoms.append(filling_atom)
            filling_atom.bondedAtoms.append(atom)

    def attempt_to_fill_antiplanar_sites(self, metal, mof):
        x_bucket = floor(metal.a * self.num_x_buckets)
        y_bucket = floor(metal.b * self.num_y_buckets)
        z_bucket = floor(metal.c * self.num_z_buckets)
        viable_zone = self.get_all_nearby_space(x_bucket, y_bucket, z_bucket)
        atoms_to_add = set()
        for possible_atom in viable_zone:
            if all(85 < Angles.degrees(Angles.angle(neighbor, metal, possible_atom, mof.angles, mof.fractional_lengths))
                   < 95 for neighbor in metal.bondedAtoms):
                distance_from_metal = Distances.distance_across_unit_cells(metal, possible_atom,
                                                                           self.angles, self.lengths)
                if distance_from_metal < CovalentRadiusLookup.lookup(metal.type_symbol) * 2.1:
                    atoms_to_add.add(possible_atom)
        if len(atoms_to_add) == 0:
            metal.open_metal_site = True
        for atom in atoms_to_add:
            metal.bondedAtoms.append(atom)
            atom.bondedAtoms.append(metal)

    def atom_near(self, spot: Atom, search_width, nonbonded_atom=None):
        x_bucket = floor(spot.a * self.num_x_buckets)
        y_bucket = floor(spot.b * self.num_y_buckets)
        z_bucket = floor(spot.c * self.num_z_buckets)
        viable_zone = self.get_all_nearby_space(x_bucket, y_bucket, z_bucket)
        for possible_atom in viable_zone:
            if nonbonded_atom is not None and possible_atom in nonbonded_atom.bondedAtoms:
                continue
            dist_from_estimate = Distances.distance_across_unit_cells(spot, possible_atom, self.angles,
                                                                      self.lengths)
            if dist_from_estimate < search_width:
                return possible_atom


    # Sometimes two metals are close enough that the algorithm says they should be bonded, but from context they
    # definitely shouldn't be bonded. The main context is when they're bonded to another atom that's in between them.
    def undo_bad_metal_bonds(self):
        metals = (atom for atom in self.atoms if atom.is_metal())
        for metal_a, metal_b in itertools.combinations(metals, 2):
            if metal_a in metal_b.bondedAtoms:
                if self.blocked_bond(metal_a, metal_b):
                    metal_a.bondedAtoms.remove(metal_b)
                    metal_b.bondedAtoms.remove(metal_a)

    def blocked_bond(self, metal_a, metal_b):
        for connecting_atom in metal_a.bondedAtoms:
            if connecting_atom.is_metal():
                continue
            if metal_b in connecting_atom.bondedAtoms:
                angle = Angles.angle(metal_a, connecting_atom, metal_b, self.angles, self.lengths)
                if angle == float('NaN'):
                    continue
                # The wider the angle, the more directly the connector is in between the metals.
                if angle > Distances.metal_bond_breakup_angle_margin:
                    return True
