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


def conversion_to_Cartesian(atom, angles, lengths):
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

    return np.matmul(matrix, np.array([atom.a, atom.b, atom.c]))


class Atom:
    def __init__(self, label, type_symbol, x, y, z, is_fractional=False):
        self.label = label
        self.type_symbol = type_symbol
        if is_fractional:
            self.a = x
            self.b = y
            self.c = z
        else:
            self.x = x
            self.y = y
            self.z = z
        self.bondedAtoms = list(())
        self.original = None  # Used when an atom is copied outside of unit cell

    @classmethod
    def from_cartesian(cls, label, type_symbol, x, y, z):
        return cls(label, type_symbol, x, y, z)

    @classmethod
    def from_fractional(cls, label, type_symbol, a, b, c, angles, lengths):
        atom = cls(label, type_symbol, a, b, c, is_fractional=True)
        (atom.x, atom.y, atom.z) = conversion_to_Cartesian(atom, angles, lengths)
        return atom

    def set_xyz_within_mof(self, mof):
        (self.x, self.y, self.z) = conversion_to_Cartesian(self, mof.angles, mof.fractional_lengths)

    def __str__(self):
        bonds_string = ''
        for atom in self.bondedAtoms:
            bonds_string = bonds_string + atom.label + ', '
        return "{name} at {x:.1f}, {y:.1f}, {z:.1f} bonded to {bonds}".format(name=self.label, x=self.x, y=self.y,
                                                                              z=self.z, bonds=bonds_string)

    def __eq__(self, other):
        return self.label == other.label

    def __hash__(self):
        return hash(self.label)

    def is_in_unit_cell(self):
        return self.original is None

    def copy_to_relative_position(self, da, db, dc, angles, lengths):
        atom = Atom.from_fractional(self.label, self.type_symbol, self.a + da, self.b + db, self.c + dc,
                                    angles, lengths)
        atom.original = self
        atom.bondedAtoms = self.bondedAtoms
        return atom
