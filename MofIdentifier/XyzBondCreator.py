from math import sqrt

from MofIdentifier.CovalentRadiusLookup import CovalentRadiusLookup
from CovalentRadiusLookup import lookup

max_bond_length = 4
# max_bond_length 5.2 is a worst-case scenario that probably won't occur in real mofs;
# a more realistic (and still cautious) value would be ~3.5
bond_length_flat_error_margin = 0.05
bond_length_multiplicative_error_margin = 1.10


def is_bond_numbered_wca(element):\
    return (element[0] == '*' or element[0] == '%' or element[0] == '#') and len(element) > 1


class XyzBondCreator:
    def __init__(self):
        self.num_compared = 0
        self.num_bonds = 0

    def is_bond_distance(self, d, a, b):
        rad_a = self.chart.lookup(a.type_symbol)
        rad_b = self.chart.lookup(b.type_symbol)
        return d < (rad_a + rad_b) * bond_length_multiplicative_error_margin + bond_length_flat_error_margin

    def connect_atoms(self, molecule):
        atoms = molecule.atoms
        for i in range(len(atoms)):
            if is_bond_numbered_wca(atoms[i].type_symbol):
                self.make_numbered_bonds(i, atoms)
                continue
            for j in range(i+1, len(atoms)):
                self.compare_for_bond(atoms[i], atoms[j])
        return molecule

    def compare_for_bond(self, atom_a, atom_b):
        self.num_compared = self.num_compared + 1
        dist = self.distance(atom_a, atom_b)
        if is_bond_numbered_wca(atom_b.type_symbol):
            pass
        elif self.is_bond_distance(dist, atom_a, atom_b):
            self.num_bonds = self.num_bonds + 1
            atom_a.bondedAtoms.append(atom_b)
            atom_b.bondedAtoms.append(atom_a)

    def distance(self, a, b):
        ax, ay, az = a.x, a.y, a.z
        bx, by, bz = b.x, b.y, b.z
        return sqrt((bx - ax) ** 2 + (by - ay) ** 2 + (bz - az) ** 2)

    def get_extra_information(self):
        return self.num_bonds, self.num_compared

    def make_numbered_bonds(self, i, atoms):
        # Connect atoms[i] to the n closest atoms
        num_bonds = int(atoms[i].type_symbol[1])
        # OtherAtom = collections.namedtuple('distance', 'index')

        other_atoms = [(self.distance(atoms[i], atoms[j]), j) for j in range(len(atoms)) if i != j]
        sorted_distances = sorted(other_atoms, key=lambda x: x[0])
        for dist_index in range(num_bonds):
            j = sorted_distances[dist_index][1]
            self.num_bonds = self.num_bonds + 1
            atoms[i].bondedAtoms.append(atoms[j])
            atoms[j].bondedAtoms.append(atoms[i])
