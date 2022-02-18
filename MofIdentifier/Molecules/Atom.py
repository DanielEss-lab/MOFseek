import math

import numpy as np

from MofIdentifier.Molecules import Coordinates

metals = {'Li', 'Be', 'Na', 'Mg', 'Al', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga',
          'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Cs', 'Ba', 'La', 'Ce',
          'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os',
          'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm',
          'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl',
          'Mc', 'Lv'}


def is_metal(type_symbol):
    return type_symbol in metals


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
            (a, b, c) = Coordinates.convert_to_fractional(x, y, z, mof)
            return cls(label, type_symbol, x, y, z, a, b, c)

    @classmethod
    def from_fractional(cls, label, type_symbol, a, b, c, angles, lengths, volume):
        return cls(label, type_symbol, *Coordinates.conversion_to_Cartesian(a, b, c, angles, lengths, volume), a, b, c)

    @classmethod
    def without_location(cls, label, type_symbol):
        return cls(label, type_symbol, float('inf'), float('inf'), float('inf'), float('inf'), float('inf'),
                   float('inf'))

    @classmethod
    def center_of(cls, atoms, mof):
        x = sum(a.x for a in atoms)/len(atoms)
        y = sum(a.y for a in atoms)/len(atoms)
        z = sum(a.z for a in atoms)/len(atoms)
        return cls.from_cartesian('Centroid', None, x, y, z, mof)

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

    def copy_to_relative_position(self, da, db, dc, angles, lengths, volume):
        atom = Atom.from_fractional(self.label, self.type_symbol, self.a + da, self.b + db, self.c + dc,
                                    angles, lengths, volume)
        atom.original = self
        atom.bondedAtoms = self.bondedAtoms
        return atom

    def copy_with_different_type(self, new_type_symbol):
        atom = Atom(self.label, new_type_symbol, self.x, self.y, self.z, self.a, self.b, self.c)
        atom.original = self
        atom.bondedAtoms = self.bondedAtoms
        return atom
