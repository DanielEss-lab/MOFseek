from math import ceil, floor, sqrt

from CovalentRadiusLookup import CovalentRadiusLookup

max_bond_length = 4
# max_bond_length 5.2 is a worst-case scenario that probably won't occur in real mofs;
# a more realistic (and still cautious) value would be ~3.5
bond_length_error_margin = 0.1


class XyzBondCreator:
    def __init__(self):
        self.chart = CovalentRadiusLookup()
        self.num_compared = 0
        self.num_bonds = 0

    def is_bond_distance(self, d, a, b):
        rad_a = self.chart.lookup(a.type_symbol)
        rad_b = self.chart.lookup(b.type_symbol)
        return d < rad_a + rad_b + bond_length_error_margin

    def connect_atoms(self, molecule):
        atoms = molecule.atoms
        for i in range(len(atoms)):
            for j in range(i+1, len(atoms)):
                self.compare_for_bond(atoms[i], atoms[j])
        return molecule

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
