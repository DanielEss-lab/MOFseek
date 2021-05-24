import numpy as np
import math

from MofIdentifier.Molecules import Molecule
from MofIdentifier.Molecules.atom import Atom


class MOF(Molecule.Molecule):
    def __init__(self, label, symmetry, a, b, c, al, be, ga):
        super().__init__(label, None)
        self.symmetry = symmetry
        self.length_a = a
        self.length_b = b
        self.length_c = c
        self.angle_alpha = al
        self.angle_beta = be
        self.angle_gamma = ga
        # Convert unit vectors to Cartesian in order to understand how basis set changes. It's a bit of a workaround TBH
        (self.length_x, n, n) = self.conversion_to_Cartesian(Atom('-', '-', 1, 0, 0, True))
        (n, self.length_y, n) = self.conversion_to_Cartesian(Atom('-', '-', 0, 1, 0, True))
        (n, n, self.length_z) = self.conversion_to_Cartesian(Atom('-', '-', 0, 0, 1, True))

    def __str__(self):
        return "{} with fractional dimensions {}, {}, {}".format(self.label,
                                                                 self.length_a, self.length_b, self.length_c)

    def set_atoms(self, atoms):
        self.atoms = atoms
        for atom in atoms:
            self.elementsPresent.add(atom.type_symbol)

    def conversion_to_Cartesian(self, atom):
        alpha = np.deg2rad(self.angle_alpha)
        beta = np.deg2rad(self.angle_beta)
        gamma = np.deg2rad(self.angle_gamma)

        value_of_trig = (np.cos(alpha) - (np.cos(beta) * np.cos(gamma))) / np.sin(gamma)

        volume_of_cell = self.length_a * self.length_b * self.length_c * math.sqrt(
            1 - (np.cos(alpha) ** 2) - (np.cos(beta) ** 2) - (np.cos(gamma) ** 2) + (
                        2 * np.cos(alpha) * np.cos(beta) * np.cos(gamma)))

        matrix = np.array([[self.length_a, (self.length_b * np.cos(gamma)), (self.length_c * np.cos(beta))],
                           [0, (self.length_b * np.sin(gamma)), self.length_c * value_of_trig],
                           [0, 0, volume_of_cell / (self.length_a * self.length_b * np.sin(gamma))]])

        # n2 = (np.cos(alpha) - np.cos(gamma) * np.cos(beta)) / np.sin(gamma)
        # M = np.array([[self.length_a, 0, 0],
        #               [self.length_b * np.cos(gamma), self.length_b * np.sin(gamma), 0],
        #               [self.length_c * np.cos(beta), self.length_c * n2, self.length_b * np.sqrt(np.sin(beta) ** 2 - n2 ** 2)]])

        return np.matmul(matrix, np.array([atom.a, atom.b, atom.c]))
