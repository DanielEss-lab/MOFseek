from collections import defaultdict
from itertools import chain

from MofIdentifier.Molecules import Molecule
from MofIdentifier.Molecules.Atom import is_metal
from MofIdentifier.bondTools import SolventTools
from MofIdentifier.fileIO.MofBondCreator import MofBondCreator
from MofIdentifier.subbuilding import SBUIdentifier
from MofIdentifier.subbuilding.SBUTools import SBUCollection


class NoMetalException(Exception):
    pass


class MOF(Molecule.Molecule):
    def __init__(self, filepath, atoms, symmetry, a, b, c, x, y, z, al, be, ga, vol, file_string, calculated_info=None):
        super().__init__(filepath, atoms)
        self.has_metal = any(is_metal(type_symbol) for type_symbol in self.elementsPresent)
        self.is_organic = any(type_symbol == 'C' for type_symbol in self.elementsPresent) and any(
            type_symbol == 'H' for type_symbol in self.elementsPresent)
        self.symmetry = symmetry
        self.fractional_lengths = (a, b, c)
        self.angles = (al, be, ga)  # alpha, beta, gamma
        self.file_content = file_string
        self.unit_volume = vol
        self.cartesian_lengths = (x, y, z)
        self._sbus = None

        if calculated_info is None:
            bond_creator = MofBondCreator(self.atoms, self.angles, self.fractional_lengths, self.cartesian_lengths,
                                          self.unit_volume)

            for x in range(1, 5):  # try 4 times
                self.open_metal_sites = bond_creator.connect_atoms()
                try:
                    components = SolventTools.get_connected_components(self.atoms)
                    atoms = []
                    self.solvents = dict()  # key: Molecule objects; value: frequency of solvent; an overview
                    self.solvent_components = []  # List of lists of atoms; every copy of every solvent
                    self.assign_components(components, atoms)
                    assert (len(atoms) > 0)
                    good_connections = True
                except NoMetalException:
                    good_connections = False
                if good_connections:
                    self.atoms = atoms
                    break
                else:
                    bond_creator.error_margin += 0.01 * x  # If 1.10 to 1.16 doesn't fix it, I'm afraid to try higher.
            else:  # no break
                assert not self.has_metal
                components = SolventTools.get_connected_components(self.atoms)
                self.assign_components(components, atoms, True)
                # If it never broke out from good_connection being True, then it never found a metal
            # Because splitting it into SBUs might result in noticing and fixing problem spots, we need to split() this
            # mof immediately in order to generate good calculated_info when needed
            if self.has_metal:
                self._sbus = SBUIdentifier.split(self, check_to_modify_bonds=True)
        else:
            atoms_by_name = {atom.label: atom for atom in self.atoms}
            (bond_information, oms_information, solvent_information, s_c_information) = calculated_info.split(';')

            bonds_to_add = [bond.split(' ') for bond in bond_information.split(',')]
            for label_a, label_b in bonds_to_add:
                atoms_by_name[label_a].bondedAtoms.append(atoms_by_name[label_b])
                atoms_by_name[label_b].bondedAtoms.append(atoms_by_name[label_a])

            self.open_metal_sites = [] if oms_information == '' else \
                [atoms_by_name[label] for label in oms_information.split(' ')]

            self.solvents = dict() if solvent_information == '' else \
                {Molecule.Molecule('solvent: no filepath',
                                   [atoms_by_name[label] for label in component.split('-')[0].split(' ')]): int(
                    component.split('-')[1]) for component in solvent_information.split(',')}

            if s_c_information == '':
                self.solvent_components = []
            else:
                self.solvent_components = [[atoms_by_name[label] for label in component.split(' ')]
                                           for component in s_c_information.split(',')]
                self.atoms = [atom for atom in self.atoms if atom not in chain.from_iterable(self.solvent_components)]

        if not self.has_metal:
            self._sbus = SBUCollection.empty()
        # self.sbu_names
        # self.identified_ligand_names

    def _exact_equals(self, o) -> bool:
        print("NOTE: this equality comparison is not efficient and should not be used in any production code")
        if not (isinstance(o, MOF) and self.has_metal == o.has_metal and self.is_organic == o.is_organic and
                self.symmetry == o.symmetry and self.fractional_lengths == o.fractional_lengths and
                self.angles == o.angles and self.file_content == o.file_content and self.unit_volume == o.unit_volume
                and self.cartesian_lengths == o.cartesian_lengths and self.filepath == o.filepath):
            return False
        try:
            for a in self.atoms:
                match = [atom for atom in o.atoms if a.label == atom.label][0]
                for b in a.bondedAtoms:
                    if b not in match.bondedAtoms:
                        return False
                for b in match.bondedAtoms:
                    if b not in a.bondedAtoms:
                        return False
        except KeyError:
            return False
        for a in o.atoms:
            if a not in self.atoms:
                return False
        for atom in self.open_metal_sites:
            if atom not in o.open_metal_sites:
                return False
        for atom in o.open_metal_sites:
            if atom not in self.open_metal_sites:
                return False
        if len(self.solvents) > 0 or len(o.solvents) > 0:
            matches = []
            for mol, freq in self.solvents.items():
                matches = [(m, f) for m, f in o.solvents.items() if freq == f and all(a in m.atoms for a in mol.atoms)
                           and len(m.atoms) == len(mol.atoms)]
            if len(matches) != 1 or len(self.solvents) != len(o.solvents):
                return False
            for atoms in self.solvent_components:
                exists_match = False
                for atoms_b in o.solvent_components:
                    if all(a in atoms_b for a in atoms) and all(a in atoms for a in atoms_b):
                        exists_match = True
                        break
                if not exists_match:
                    return False
        return True

    def near_equals(self, o) -> bool:
        if not (isinstance(o, MOF) and self.symmetry == o.symmetry and self.fractional_lengths == o.fractional_lengths
                and self.angles == o.angles):
            return False
        element_and_num_bonds_frequency_imbalance = defaultdict(lambda: 0)
        for a in self.atoms:
            element_and_num_bonds_frequency_imbalance[f"{a.type_symbol}{len(a.bondedAtoms)}"] += 1
        for a in o.atoms:
            element_and_num_bonds_frequency_imbalance[f"{a.type_symbol}{len(a.bondedAtoms)}"] -= 1
        for freq in element_and_num_bonds_frequency_imbalance.values():
            if freq != 0:
                return False
        return True

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

    def assign_components(self, components, atoms, allow_no_metal=False):
        atoms.extend(components[0])
        if not allow_no_metal:
            has_metal = False
            for atom in atoms:
                if atom.is_metal():
                    has_metal = True
                    break
            if not has_metal:
                raise NoMetalException
        for comp_index in range(1, len(components)):
            if len(components[comp_index]) < len(atoms) and not any(atom.is_metal() for atom in components[comp_index]):
                self.solvent_components = components[comp_index:]
                self.solvents = SolventTools.count_solvents(self.solvent_components)
                return
            else:
                atoms.extend(components[comp_index])

    def get_calculated_info_string(self):
        bonds = set()
        for atom in self.atoms + list(chain.from_iterable(self.solvent_components)):
            for n in atom.bondedAtoms:
                bond_code = f'{atom.label} {n.label}' if atom.label < n.label else f'{n.label} {atom.label}'
                bonds.add(bond_code)
        bond_information = ','.join(bonds)

        oms_information = ' '.join(atom.label for atom in self.open_metal_sites)

        solvent_information = ','.join(
            f"{' '.join(atom.label for atom in mol.atoms)}-{freq}" for mol, freq in self.solvents.items())

        s_c_information = ','.join(' '.join(atom.label for atom in component) for component in self.solvent_components)

        return ';'.join([bond_information, oms_information, solvent_information, s_c_information])
