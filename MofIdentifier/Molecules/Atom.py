import math

import numpy as np

metals = {'Li', 'Be', 'Na', 'Mg', 'Al', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga',
          'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Cs', 'Ba', 'La', 'Ce',
          'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os',
          'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm',
          'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl',
          'Mc', 'Lv'}


def is_metal(type_symbol):
    return type_symbol in metals


def conversion_to_Cartesian(atom_a, atom_b, atom_c, angles, lengths):
    alpha = np.deg2rad(angles[0])
    beta = np.deg2rad(angles[1])
    gamma = np.deg2rad(angles[2])
    length_a = lengths[0]
    length_b = lengths[1]
    length_c = lengths[2]

    value_of_trig = (np.cos(alpha) - (np.cos(beta) * np.cos(gamma))) / np.sin(gamma)

    volume_of_cell = length_a * length_b * length_c * math.sqrt(
        1 - (np.cos(alpha) ** 2) - (np.cos(beta) ** 2) - (np.cos(gamma) ** 2) + (
                2 * np.cos(alpha) * np.cos(beta) * np.cos(gamma)))

    matrix = np.array([[length_a, (length_b * np.cos(gamma)), (length_c * np.cos(beta))],
                       [0, (length_b * np.sin(gamma)), length_c * value_of_trig],
                       [0, 0, volume_of_cell / (length_a * length_b * np.sin(gamma))]])

    return np.matmul(matrix, np.array([atom_a, atom_b, atom_c]))


def convert_to_fractional(atom_x, atom_y, atom_z, mof):
    alpha = np.deg2rad(mof.angles[0])
    beta = np.deg2rad(mof.angles[1])
    gamma = np.deg2rad(mof.angles[2])
    a = mof.fractional_lengths[0]
    b = mof.fractional_lengths[1]
    c = mof.fractional_lengths[2]
    omega = mof.unit_volume
    conversion_matrix = np.array([[1 / a, -np.cos(gamma) / (a * np.sin(gamma)),
                                   b * c * (np.cos(alpha) * np.cos(gamma) - np.cos(beta)) / (omega * np.sin(gamma))],
                                  [0, 1 / (b * np.sin(gamma)),
                                   a * c * (np.cos(beta) * np.cos(gamma) - np.cos(alpha)) / (omega * np.sin(gamma))],
                                  [0, 0, a * b * np.sin(gamma) / omega]])
    return np.matmul(conversion_matrix, np.array([atom_x, atom_y, atom_z]))


class Atom:
    def __init__(self, label, type_symbol, x, y, z, a, b, c):
        self.label = label
        self.type_symbol = type_symbol
        self.a = a
        self.b = b
        self.c = c
        self.x = x
        self.y = y
        self.z = z
        self.bondedAtoms = list(())
        self.original = None  # Used when an atom is copied outside of unit cell
        self.is_bond_limited = False
        self.open_metal_site = False

    @classmethod
    def from_cartesian(cls, label, type_symbol, x, y, z, mof=None):
        if mof is None:
            return cls(label, type_symbol, x, y, z, float('inf'), float('inf'), float('inf'))
        else:
            (a, b, c) = convert_to_fractional(x, y, z, mof)
            return cls(label, type_symbol, x, y, z, a, b, c)

    @classmethod
    def from_fractional(cls, label, type_symbol, a, b, c, angles, lengths):
        (x, y, z) = conversion_to_Cartesian(a, b, c, angles, lengths)
        return cls(label, type_symbol, x, y, z, a, b, c)

    @classmethod
    def without_location(cls, label, type_symbol):
        return cls(label, type_symbol, float('inf'), float('inf'), float('inf'), float('inf'), float('inf'),
                   float('inf'))

    def __str__(self):
        bonds_string = ''
        for atom in self.bondedAtoms:
            bonds_string = bonds_string + atom.label + ', '
        return "{name} at {x:.1f}, {y:.1f}, {z:.1f} bonded to {bonds}".format(name=self.label, x=self.x, y=self.y,
                                                                              z=self.z, bonds=bonds_string)

    def __eq__(self, other):
        return self.label == other.label

    def __lt__(self, other):
        return self.label < other.label

    def __hash__(self):
        return hash(self.label)

    def is_metal(self):
        return self.type_symbol in metals

    def is_in_unit_cell(self):
        return self.original is None

    def copy_to_relative_position(self, da, db, dc, angles, lengths):
        atom = Atom.from_fractional(self.label, self.type_symbol, self.a + da, self.b + db, self.c + dc,
                                    angles, lengths)
        atom.original = self
        atom.bondedAtoms = self.bondedAtoms
        return atom
