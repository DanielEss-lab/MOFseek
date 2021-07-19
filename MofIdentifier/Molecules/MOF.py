from MofIdentifier.Molecules import Molecule
from MofIdentifier.Molecules.atom import conversion_to_Cartesian
from MofIdentifier.bondTools import SolventTools
from MofIdentifier.fileIO.MofBondCreator import MofBondCreator
from MofIdentifier.subbuilding import SBUIdentifier


class MOF(Molecule.Molecule):
    def __init__(self, filepath, atoms, symmetry, a, b, c, al, be, ga, file_string):
        super().__init__(filepath, atoms)
        self.symmetry = symmetry
        self.fractional_lengths = (a, b, c)
        self.angles = (al, be, ga)  # alpha, beta, gamma
        self.file_content = file_string
        (length_x, n, n) = conversion_to_Cartesian(1, 0, 0, (al, be, ga), (a, b, c))
        (n, length_y, n) = conversion_to_Cartesian(0, 1, 0, (al, be, ga), (a, b, c))
        (n, n, length_z) = conversion_to_Cartesian(0, 0, 1, (al, be, ga), (a, b, c))
        self.unit_volume = length_x * length_y * length_z
        self.cartesian_lengths = (length_x, length_y, length_z)

        bond_creator = MofBondCreator(self.atoms, self.angles, self.fractional_lengths, self.cartesian_lengths)
        bond_creator.connect_atoms()
        self._sbus = None

        components = SolventTools.get_connected_components(atoms)
        self.atoms = []
        self.solvents = dict()
        self.assign_components(components, self.atoms, self.solvents)

        # self.sbu_names
        # self.identified_ligand_names

    def sbus(self):
        if self._sbus is None:
            self._sbus = SBUIdentifier.split(self)
        return self._sbus

    def __str__(self):
        return "{} with fractional dimensions {}".format(self.label, self.fractional_lengths)

    def assign_components(self, components, atoms, solvents):
        atoms.extend(components[0])
        for comp_index in range(1, len(components)):
            if len(components[comp_index]) < 8 and len(components[comp_index]) * 2 < len(components[0]):
                self.solvents = SolventTools.count_solvents(components[comp_index:])
                return
            else:
                atoms.extend(components[comp_index])
