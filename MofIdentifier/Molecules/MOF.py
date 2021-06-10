import math

import numpy as np

from MofIdentifier.Molecules import Molecule
from MofIdentifier.Molecules.atom import conversion_to_Cartesian
from MofIdentifier.fileIO.MofBondCreator import MofBondCreator
from MofIdentifier.subbuilding import SBUIdentifier


class MOF(Molecule.Molecule):
    def __init__(self, filepath, atoms, symmetry, a, b, c, al, be, ga, file_string):
        super().__init__(filepath, atoms)
        self.symmetry = symmetry
        self.fractional_lengths = (a, b, c)
        self.angles = (al, be, ga)
        self.cif_content = file_string
        self.unit_volume = a * b * c * math.sqrt(1 + 2 * math.cos(np.deg2rad(al)) * math.cos(np.deg2rad(be))
                                                 * math.cos(np.deg2rad(ga)) - math.cos(np.deg2rad(al)) ** 2 -
                                                 math.cos(np.deg2rad(be)) ** 2 - math.cos(np.deg2rad(ga)) ** 2)
        # Convert unit vectors to Cartesian in order to understand how basis set changes. It's a bit of a workaround TBH
        (length_x, n, n) = conversion_to_Cartesian(1, 0, 0, (al, be, ga), (a, b, c))
        (n, length_y, n) = conversion_to_Cartesian(0, 1, 0, (al, be, ga), (a, b, c))
        (n, n, length_z) = conversion_to_Cartesian(0, 0, 1, (al, be, ga), (a, b, c))
        self.cartesian_lengths = (length_x, length_y, length_z)

        bond_creator = MofBondCreator(self.atoms, self.angles, self.fractional_lengths, self.cartesian_lengths)
        bond_creator.connect_atoms()
        self._sbus = None

    def sbus(self):
        if self._sbus is None:
            self._sbus = SBUIdentifier.split(self)
        return self._sbus

    def __str__(self):
        return "{} with fractional dimensions {}".format(self.label, self.fractional_lengths)
