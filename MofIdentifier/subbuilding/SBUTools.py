from collections import deque
from enum import Enum
from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.fileIO import XyzBondCreator


class SBUCollection:
    def __init__(self, clusters, connectors, auxiliaries):
        self.clusters = clusters
        self.connectors = connectors
        self.auxiliaries = auxiliaries

    def __str__(self):
        string = ""
        if len(self.clusters) > 0:
            string += "Clusters:"
            for cluster in self.clusters:
                string += "\n" + cluster.__str__()
            string += "\n"
        if len(self.connectors) > 0:
            string += "Connectors:"
            for connector in self.connectors:
                string += "\n" + connector.__str__()
            string += "\n"
        if len(self.auxiliaries) > 0:
            string += "Auxiliaries:"
            for auxiliary in self.auxiliaries:
                string += "\n" + auxiliary.__str__()
            string += "\n"
        return string


class UnitType(Enum):
    CLUSTER = 1
    CONNECTOR = 2
    AUXILIARY = 3

    def __str__(self):
        return "cluster" if self == UnitType.CLUSTER else "connector" if self == UnitType.CONNECTOR else "auxiliary"


class SBU:
    def __init__(self, sbu_id, unit_type, atoms):
        self.sbu_id = sbu_id
        self.adjacent_cluster_ids = set(())
        self.adjacent_connector_ids = set(())
        self.adjacent_auxiliary_ids = set(())
        self.type = unit_type
        self.atoms = atoms
        self.frequency = 1
        self.label = 'Unlabeled'
        self.should_use_weak_comparison = False

    def normalize_atoms(self, mof):
        atoms = []
        for atom in self.atoms:
            while not atom.is_in_unit_cell():
                atom = atom.original
            atoms.append(atom)
        starting_atom = atoms[0]  # Get an atom, any atom
        visited = {starting_atom}
        queue = deque([starting_atom])
        while queue:
            atom = queue.popleft()
            for neighbor in (n for n in atom.bondedAtoms if n in atoms and n not in visited):
                d = XyzBondCreator.distance(atom, neighbor)
                if not XyzBondCreator.is_bond_distance(d, atom, neighbor):
                    if neighbor.a - atom.a > 0.5:
                        neighbor.a -= 1.0
                    elif neighbor.a - atom.a < -0.5:
                        neighbor.a += 1.0
                    if neighbor.b - atom.b > 0.5:
                        neighbor.b -= 1.0
                    elif neighbor.b - atom.b < -0.5:
                        neighbor.b += 1.0
                    if neighbor.c - atom.c > 0.5:
                        neighbor.c -= 1.0
                    elif neighbor.c - atom.c < -0.5:
                        neighbor.c += 1.0
                    neighbor.set_xyz_within_mof(mof)
                visited.add(neighbor)
                queue.append(neighbor)
        self.atoms = visited

    def __str__(self):
        elements = dict()
        for atom in self.atoms:
            if atom.type_symbol in elements:
                elements[atom.type_symbol] += 1
            else:
                elements[atom.type_symbol] = 1
        atoms_string = ''
        for element in elements:
            atoms_string = atoms_string + str(elements[element]) + element + ' '
        unit = str(self.type)
        return "{freq}x {label}: {atoms}({atom_n} atom {unittype}) each bonded to {cluster} clusters, {connector} " \
               "connectors, and {aux} auxiliary groups".format(label=self.label, freq=self.frequency,
                                                               atoms=atoms_string, atom_n=len(self.atoms),
                                                               unittype=unit, cluster=len(self.adjacent_cluster_ids),
                                                               connector=len(self.adjacent_connector_ids),
                                                               aux=len(self.adjacent_auxiliary_ids))

    def __eq__(self, other):
        is_isomorphic = SubGraphMatcher.match(self, other)
        return is_isomorphic and len(self.adjacent_connector_ids) == len(other.adjacent_connector_ids) \
            and len(self.adjacent_cluster_ids) == len(other.adjacent_cluster_ids) \
            and len(self.adjacent_auxiliary_ids) == len(other.adjacent_auxiliary_ids)

    def graph_equals(self, other):
        return len(self.atoms) == len(other.atoms) and SubGraphMatcher.match(self, other)
