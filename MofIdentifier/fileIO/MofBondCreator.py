import itertools
from math import floor

from MofIdentifier.bondTools import Distances, OpenMetalSites, CovalentRadiusLookup, Angles
from collections import namedtuple
from MofIdentifier.Molecules.Atom import Atom

max_bond_length = 4.1


# max_bond_length 5.2 is a worst-case scenario that probably won't occur in most real mofs;
# a more realistic (and still cautious) value would be ~3.5


class MofBondCreator:
    def __init__(self, atoms, angles, fractional_lengths, cartesian_lengths, volume):
        Moflike = namedtuple('Moflike', 'fractional_lengths angles unit_volume')
        self.angles = angles
        self.lengths = fractional_lengths
        self.atoms: list[Atom] = atoms
        self.volume = volume
        self.mof = Moflike(self.lengths, self.angles, self.volume)
        # Floor the number of buckets to overestimate the size of buckets
        # to ensure we're comparing at all viable distances
        self.num_x_buckets = floor(cartesian_lengths[0] / max_bond_length) if cartesian_lengths[
                                                                                  0] > max_bond_length else 1
        self.num_y_buckets = floor(cartesian_lengths[1] / max_bond_length) if cartesian_lengths[
                                                                                  1] > max_bond_length else 1
        self.num_z_buckets = floor(cartesian_lengths[2] / max_bond_length) if cartesian_lengths[
                                                                                  2] > max_bond_length else 1
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
        # First processing
        if self.error_margin != Distances.bond_length_multiplicative_error_margin:
            self.reset()
        for z in range(self.num_z_buckets):
            for y in range(self.num_y_buckets):
                for x in range(self.num_x_buckets):
                    this_space = self.cellSpace[z][y][x]
                    spaces_to_compare = self.get_spaces_adj_in_one_direction(z, y, x)
                    self.connect_within_space(this_space)
                    self.connect_within_spaces(this_space, spaces_to_compare)
        # Going back to fix funky areas
        self.enforce_single_hydrogen_bonds()
        self.enfore_OCO_consistency()
        open_metal_sites = self.fill_nearly_closed_metal_sites()
        return open_metal_sites

    def get_spaces_adj_in_one_direction(self, z, y, x):
        # in 2D space, you only need to compare each square with 4 other squares in order for each square
        # to be compared with all 8 adjacent (including diagonals) neighbors. For example, if you compare
        # each square with the square to its right, you don't also need to compare each square with the square to
        # its left. The following code makes use of that principle except in 3Dspace. These 13, their opposites,
        # and the cube itself comprise the entire 3x3x3 region. This way, no comparison happens twice.
        near_space = self.get_bucket(z, y, x + 1) \
                     + self.get_bucket(z, y + 1, x) \
                     + self.get_bucket(z + 1, y, x) \
                     + self.get_bucket(z, y + 1, x + 1) \
                     + self.get_bucket(z + 1, y, x + 1) \
                     + self.get_bucket(z + 1, y + 1, x) \
                     + self.get_bucket(z + 1, y + 1, x + 1) \
                     + self.get_bucket(z - 1, y, x + 1) \
                     + self.get_bucket(z - 1, y + 1, x + 1) \
                     + self.get_bucket(z - 1, y + 1, x) \
                     + self.get_bucket(z, y + 1, x - 1) \
                     + self.get_bucket(z + 1, y - 1, x + 1) \
                     + self.get_bucket(z + 1, y + 1, x - 1)
        return near_space

    def get_all_nearby_space(self, x, y, z):
        near_space = self.get_bucket(z, y, x) \
                     + self.get_bucket(z, y, x + 1) + self.get_bucket(z, y, x - 1) \
                     + self.get_bucket(z, y + 1, x) + self.get_bucket(z, y - 1, x) \
                     + self.get_bucket(z + 1, y, x) + self.get_bucket(z - 1, y, x) \
                     + self.get_bucket(z, y + 1, x + 1) + self.get_bucket(z, y - 1, x - 1) \
                     + self.get_bucket(z + 1, y, x + 1) + self.get_bucket(z - 1, y, x - 1) \
                     + self.get_bucket(z + 1, y + 1, x) + self.get_bucket(z - 1, y - 1, x) \
                     + self.get_bucket(z + 1, y + 1, x + 1) + self.get_bucket(z - 1, y - 1, x - 1) \
                     + self.get_bucket(z - 1, y, x + 1) + self.get_bucket(z + 1, y, x - 1) \
                     + self.get_bucket(z - 1, y + 1, x + 1) + self.get_bucket(z + 1, y - 1, x - 1) \
                     + self.get_bucket(z - 1, y + 1, x) + self.get_bucket(z + 1, y - 1, x) \
                     + self.get_bucket(z, y + 1, x - 1) + self.get_bucket(z, y - 1, x + 1) \
                     + self.get_bucket(z + 1, y - 1, x + 1) + self.get_bucket(z - 1, y + 1, x - 1) \
                     + self.get_bucket(z + 1, y + 1, x - 1) + self.get_bucket(z - 1, y - 1, x + 1)
        return near_space

    def connect_within_space(self, space):
        for i in range(len(space)):
            for j in range(i + 1, len(space)):
                self.compare_for_bond(space[i], space[j])

    def connect_within_spaces(self, space_a, space_b):
        for atom_a in space_a:
            for atom_b in space_b:
                self.compare_for_bond(atom_a, atom_b)

    def compare_for_bond(self, atom_a, atom_b, known_to_be_adjacent_spaces=True):
        if atom_b in atom_a.bondedAtoms:
            return
        dist = Distances.distance(atom_a, atom_b) if known_to_be_adjacent_spaces \
            else Distances.distance_across_unit_cells(atom_a, atom_b, self.angles, self.lengths)
        if Distances.is_bond_distance(dist, atom_a, atom_b, self.error_margin):
            if not self.is_blocked_bond(atom_a, atom_b):
                atom_a.bondedAtoms.append(atom_b)
                atom_b.bondedAtoms.append(atom_a)
                self.break_blocked_bonds(atom_a, atom_b)

    def is_blocked_bond(self, atom_a, atom_b):
        # Sometimes two atoms are close enough that distance says they should be bonded, but from context they
        # clearly shouldn't be bonded, ie when they're bonded to another atom that's in between them.
        triangling_atoms = [Distances.move_neighbor_if_distant(atom_a, atom, self.angles, self.lengths)
                            for atom in atom_a.bondedAtoms if atom in atom_b.bondedAtoms]
        between_atoms = {atom: Angles.mof_angle(atom_a, atom, atom_b, self.angles, self.lengths) for atom in
                         triangling_atoms if Angles.mof_angle(atom_a, atom, atom_b, self.angles, self.lengths) >
                         Angles.max_bond_breakup_angle}
        # The wider the angle, the more directly the connector is in between the metals.
        if len(between_atoms) > 0:
            if any(angle > Angles.bond_breakup_angle for angle in between_atoms.values()):
                return True
            if len(between_atoms) > 1:
                # try combining the best two, then best three, etc. to see if their combined locations block the bond
                possible_blocks = list(between_atoms.items())
                possible_blocks.sort(key=lambda e: e[1], reverse=True)
                for i in range(1, len(between_atoms)):
                    best_blocks_here = [tup[0] for tup in possible_blocks[0:i + 1]]
                    center = Atom.center_of(best_blocks_here, self.mof)
                    if Angles.mof_angle(atom_a, center, atom_b, self.angles, self.lengths) > \
                            Angles.bond_breakup_angle:
                        return True
        return False

    def break_blocked_bonds(self, atom_a, atom_b):
        # if adding a bond between atom a and atom b has caused a previously established bond to be blocked
        # (as per definition of blocked_bond() above), we need to undo that previous bond.
        triangling_atoms = [Distances.move_neighbor_if_distant(atom_a, atom, self.angles, self.lengths)
                            for atom in atom_a.bondedAtoms if atom in atom_b.bondedAtoms]
        for atom in triangling_atoms:
            if self.is_blocked_bond(atom_a, atom):
                atom_a.bondedAtoms.remove(atom)
                atom.bondedAtoms.remove(atom_a)
            elif self.is_blocked_bond(atom_b, atom):
                atom_b.bondedAtoms.remove(atom)
                atom.bondedAtoms.remove(atom_b)

    def enforce_single_hydrogen_bonds(self):
        for atom in self.atoms:
            if atom.type_symbol == 'H' and len(atom.bondedAtoms) > 1:
                close_atoms = atom.bondedAtoms.copy()
                self.remove_distant_bonds(atom)
                # Adding the H to the second molecule might have broken a bond between molecules that should be bonded
                # now that the H is only bonded to one. Let's check that here:
                for atom_a, atom_b in itertools.combinations(close_atoms, 2):
                    self.compare_for_bond(atom_a, atom_b, False)

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

    # A certain pattern at the end of linkers has a carbon attached to two oxygen, which are attached to a metal.
    # Sometimes, one of the O-metal distances is a tad too long for the algorithm to catch. This fixes that.
    def enfore_OCO_consistency(self):
        for atom in self.atoms:
            if atom.type_symbol == 'O' and len(atom.bondedAtoms) == 2:
                metals = [a for a in atom.bondedAtoms if a.is_metal()]
                carbons = [a for a in atom.bondedAtoms if a.type_symbol == 'C']
                if len(metals) != 1 or len(carbons) != 1:
                    continue
                carbon = carbons[0]
                metal = metals[0]
                if len(carbon.bondedAtoms) == 3:
                    other_oxygens = [a for a in carbon.bondedAtoms if a.type_symbol == 'O' and a.label != atom.label]
                    if len(other_oxygens) != 1:
                        continue
                    oxygen = other_oxygens[0]
                else:
                    continue
                if metal not in oxygen.bondedAtoms and oxygen not in metal.bondedAtoms:
                    distance = Distances.distance_across_unit_cells(metal, oxygen, self.angles, self.lengths)
                    required_distance = Distances.bond_distance(metal, oxygen, self.error_margin + 0.2)
                    if distance <= required_distance:
                        oxygen.bondedAtoms.append(metal)
                        metal.bondedAtoms.append(oxygen)

    def reset(self):
        for atom in self.atoms:
            atom.bondedAtoms = []

    # Sometimes a particular bond is larger than I can stretch my algorithms to allow, but is clearly there. The main
    # indicator of this is asymmetry in a metal's bonds, where it may see that there is an open metal site but really
    # there's simply an atom that the metal is bonding but the algorithm didn't catch.
    def fill_nearly_closed_metal_sites(self):
        open_metal_sites = list()
        open_site_metals = (atom for atom in self.atoms if OpenMetalSites.has_open_metal_site(atom, self.mof))
        for atom in open_site_metals:
            if len(atom.bondedAtoms) == 0:
                continue
            if len(atom.bondedAtoms) == 4 and OpenMetalSites.square_planar_angles(atom, self.mof):
                self.attempt_to_fill_antiplanar_sites(atom, self.mof)
            else:
                self.attempt_to_fill_countercenter_site(atom, self.mof)
            if atom.open_metal_site:
                open_metal_sites.append(atom)
        return open_metal_sites

    def attempt_to_fill_countercenter_site(self, atom, mof):
        # length = twice the covalent radius of the atom
        search_radius = CovalentRadiusLookup.lookup(atom.type_symbol) * 3 / 8
        geom_center, mass_center = OpenMetalSites.centers_of_bonded_atoms(atom, self.mof)
        metal_to_center_distance = Distances.distance_across_unit_cells(atom, geom_center, self.angles, self.lengths)
        if metal_to_center_distance < 0.05 and len(atom.bondedAtoms) < 4:
            atom.open_metal_site = True
            return  # If there's only 3 atoms bonded, and they're rather symmetric, then don't stretch to find a 4th
        farthest_center, other_center = (geom_center, mass_center) \
                if metal_to_center_distance > Distances.distance_across_unit_cells(atom, mass_center, self.angles, self.lengths) \
                else (mass_center, geom_center)

        estimate = OpenMetalSites.estimated_bond_site(atom, farthest_center, mof)
        filling_atom = self.non_h_atom_near(estimate, search_radius)
        if filling_atom is None:
            if self.angles_allow_adding_atom(atom, estimate):
                atom.open_metal_site = True
                return
        elif filling_atom not in atom.bondedAtoms:
            atom.bondedAtoms.append(filling_atom)
            filling_atom.bondedAtoms.append(atom)
            # do everything OMS-related for this atom again now that it's changed
            if OpenMetalSites.has_open_metal_site(atom, self.mof):
                if len(atom.bondedAtoms) == 4 and OpenMetalSites.square_planar_angles(atom, self.mof):
                    self.attempt_to_fill_antiplanar_sites(atom, self.mof)
                else:
                    self.attempt_to_fill_countercenter_site(atom, self.mof)

        estimate = OpenMetalSites.estimated_bond_site(atom, other_center, mof)
        filling_atom = self.non_h_atom_near(estimate, search_radius)
        if filling_atom is None:
            if self.angles_allow_adding_atom(atom, estimate):
                atom.open_metal_site = True
                return
        elif filling_atom not in atom.bondedAtoms:
            atom.bondedAtoms.append(filling_atom)
            filling_atom.bondedAtoms.append(atom)
            # do everything OMS-related for this atom again now that it's changed
            if OpenMetalSites.has_open_metal_site(atom, self.mof):
                if len(atom.bondedAtoms) == 4 and OpenMetalSites.square_planar_angles(atom, self.mof):
                    self.attempt_to_fill_antiplanar_sites(atom, self.mof)
                else:
                    self.attempt_to_fill_countercenter_site(atom, self.mof)

    def angles_allow_adding_atom(self, atom, estimate):
        angles = [Angles.mof_angle(neighbor, atom, estimate, self.angles, self.lengths) for neighbor in
                  atom.bondedAtoms]
        angles.sort()
        return len(angles) < 2 or (angles[0] + angles[1]) / 2 > Angles.bond_coexistance_angle

    def attempt_to_fill_antiplanar_sites(self, metal, mof):
        x_bucket = floor(metal.a * self.num_x_buckets)
        y_bucket = floor(metal.b * self.num_y_buckets)
        z_bucket = floor(metal.c * self.num_z_buckets)
        viable_zone = self.get_all_nearby_space(x_bucket, y_bucket, z_bucket)
        atoms_to_add = set()
        for possible_atom in viable_zone:
            if possible_atom.type_symbol == 'H':
                continue
            if all(80 < Angles.degrees(
                    Angles.mof_angle(neighbor, metal, possible_atom, mof.angles, mof.fractional_lengths))
                   < 100 for neighbor in metal.bondedAtoms):
                distance_from_metal = Distances.distance_across_unit_cells(metal, possible_atom,
                                                                           self.angles, self.lengths)
                if distance_from_metal < CovalentRadiusLookup.lookup(metal.type_symbol) * 2.1:
                    atoms_to_add.add(possible_atom)
        if len(atoms_to_add) < 2:
            metal.open_metal_site = True
        for atom in atoms_to_add:
            metal.bondedAtoms.append(atom)
            atom.bondedAtoms.append(metal)

    def non_h_atom_near(self, spot: Atom, search_width):
        x_bucket = floor(spot.a * self.num_x_buckets)
        y_bucket = floor(spot.b * self.num_y_buckets)
        z_bucket = floor(spot.c * self.num_z_buckets)
        viable_zone = self.get_all_nearby_space(x_bucket, y_bucket, z_bucket)
        best_dist = search_width
        best_atom = None
        for possible_atom in viable_zone:
            if possible_atom.type_symbol == 'H':
                continue
            dist_from_estimate = Distances.distance_across_unit_cells(spot, possible_atom, self.angles,
                                                                      self.lengths)
            if dist_from_estimate < best_dist:
                best_dist = dist_from_estimate
                best_atom = possible_atom
        return best_atom
