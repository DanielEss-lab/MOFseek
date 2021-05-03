from math import ceil, floor, sqrt

from CovalentRadiusLookup import CovalentRadiusLookup

max_bond_length = 4
# max_bond_length 5.2 is a worst-case scenario that probably won't occur in real mofs;
# a more realistic (and still cautious) value would be ~3.5
bond_length_error_margin = 0.1


class MofBondCreator:
    def __init__(self, mof):
        self.chart = CovalentRadiusLookup()
        self.num_x_buckets = ceil(mof.length_a / max_bond_length)
        self.num_y_buckets = ceil(mof.length_b / max_bond_length)
        self.num_z_buckets = ceil(mof.length_c / max_bond_length)
        (self.length_a, self.length_b, self.length_c) = (mof.length_a, mof.length_b, mof.length_c)
        self.cellSpace = [[[list(()) for a in range(self.num_x_buckets)] for b in range(self.num_y_buckets)]
                          for c in range(self.num_z_buckets)]
        for atom in mof.atoms:
            x_bucket = floor(atom.x / max_bond_length)
            y_bucket = floor(atom.y / max_bond_length)
            z_bucket = floor(atom.z / max_bond_length)
            self.cellSpace[z_bucket][y_bucket][x_bucket].append(atom)
        self.num_compared = 0
        self.num_bonds = 0

    def is_bond_distance(self, d, a, b):
        rad_a = self.chart.lookup(a.type_symbol)
        rad_b = self.chart.lookup(b.type_symbol)
        return d < rad_a + rad_b + bond_length_error_margin

    def get_bucket(self, z, y, x):
        bucket_belongs_to_unit_cell = True
        dx, dy, dz = 0, 0, 0
        if 0 <= z < self.num_z_buckets:
            plane = self.cellSpace[z]
        else:
            bucket_belongs_to_unit_cell = False
            plane = self.cellSpace[z % self.num_z_buckets]
            dz = self.length_c * (1 if z > 0 else -1)
        if 0 <= y < self.num_y_buckets:
            row = plane[y]
        else:
            bucket_belongs_to_unit_cell = False
            row = plane[y % self.num_y_buckets]
            dy = self.length_b * (1 if y > 0 else -1)
        if 0 <= x < self.num_x_buckets:
            bucket = row[x]
        else:
            bucket_belongs_to_unit_cell = False
            bucket = row[x % self.num_x_buckets]
            dx = self.length_a * (1 if x > 0 else -1)

        if bucket_belongs_to_unit_cell:
            return bucket
        else:
            bucket_copy = list(())
            for atom in bucket:
                bucket_copy.append(atom.copy_to_relative_position(dx, dy, dz))
            return bucket_copy

    def connect_atoms(self):
        for z in range(self.num_z_buckets):
            for y in range(self.num_y_buckets):
                for x in range(self.num_x_buckets):
                    this_space = self.cellSpace[z][y][x]
                    spaces_to_compare = self.get_spaces_adj_in_one_direction(x, y, z)
                    self.connect_within_space(this_space)
                    self.connect_within_spaces(this_space, spaces_to_compare)

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

    def connect_within_space(self, space):
        for i in range(len(space)):
            for j in range(i+1, len(space)):
                self.compare_for_bond(space[i], space[j])


    def connect_within_spaces(self, space_a, space_b):
        for atom_a in space_a:
            for atom_b in space_b:
                self.compare_for_bond(atom_a, atom_b)

    def compare_for_bond(self, atom_a, atom_b):
        self.num_compared = self.num_compared + 1
        dist = self.distance(atom_a, atom_b)
        if self.is_bond_distance(dist, atom_a, atom_b):
            self.num_bonds = self.num_bonds + 1
            atom_a.bondedAtoms.append(atom_b)
            atom_b.bondedAtoms.append(atom_a)

    def distance(self, a, b):
        ax, ay, az = a.x, a.y, a.z
        bx, by, bz = b.x, b.y, b.z
        return sqrt((bx - ax) ** 2 + (by - ay) ** 2 + (bz - az) ** 2)

    def get_extra_information(self):
        return self.num_bonds, self.num_compared