from MofIdentifier.Molecules import Molecule
from MofIdentifier.Molecules.atom import conversion_to_Cartesian
from MofIdentifier.bondTools import SolventTools
from MofIdentifier.fileIO.MofBondCreator import MofBondCreator
from MofIdentifier.subbuilding import SBUIdentifier


class NoMetalException(Exception):
    pass


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
        self._sbus = None

        for x in range(1, 4):  # try 3 times
            bond_creator.connect_atoms()
            try:
                components = SolventTools.get_connected_components(self.atoms)
                self.atoms = []
                self.solvents = dict()
                self.solvent_components = []
                self.assign_components(components, self.atoms)
                assert (len(atoms) > 0)
                good_connections = True
            except NoMetalException:
                good_connections = False
            if good_connections:
                break
            else:
                bond_creator.error_margin += 0.01 * x  # If 1.10 to 1.16 doesn't fix it, I'm afraid to try higher.
        else:  # no break
            raise NoMetalException  # If it never broke out from good_connection being True, then it's a problem MOF

        # self.sbu_names
        # self.identified_ligand_names

    def atoms_string_with_solvents(self):
        string = ''
        elements = list(self.elementsPresent)
        elements.sort()
        for element in elements:
            string = string + str(self.elementsPresent[element]) + ' ' + element + ',  '
        return string[0:-3]

    def atoms_string_without_solvents(self):
        if len(self.solvents) == 0:
            return self.atoms_string_with_solvents()
        elementsPresent = dict()
        for atom in self.atoms:
            if atom.type_symbol in elementsPresent:
                elementsPresent[atom.type_symbol] += 1
            else:
                elementsPresent[atom.type_symbol] = 1
        string = ''
        elements = list(elementsPresent)
        elements.sort()
        for element in elements:
            string = string + str(elementsPresent[element]) + ' ' + element + ',  '
        return string[0:-3]

    def sbus(self):
        if self._sbus is None:
            self._sbus = SBUIdentifier.split(self)
        return self._sbus

    def __str__(self):
        return "{} with fractional dimensions {}".format(self.label, self.fractional_lengths)

    def assign_components(self, components, atoms):
        atoms.extend(components[0])
        has_metal = False
        for atom in atoms:
            if atom.is_metal():
                has_metal = True
                break
        if not has_metal:
            raise NoMetalException
        for comp_index in range(1, len(components)):
            if len(components[comp_index]) < 13 and len(components[comp_index]) * 2 < len(components[0]):
                self.solvent_components = components[comp_index:]
                self.solvents = SolventTools.count_solvents(self.solvent_components)
                return
            else:
                atoms.extend(components[comp_index])
