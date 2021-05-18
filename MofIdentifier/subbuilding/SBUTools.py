from collections import deque
from enum import Enum
from MofIdentifier import SubGraphMatcher
from MofIdentifier.fileIO import XyzBondCreator


class SBUs:
    def __init__(self, clusters, connectors, auxiliaries):
        self.clusters = clusters
        self.connectors = connectors
        self.auxiliaries = auxiliaries

    def __str__(self):
        string = "Clusters:"
        for cluster in self.clusters:
            string += "\n" + cluster.__str__()
        string += "\nConnectors:"
        for connector in self.connectors:
            string += "\n" + connector.__str__()
        string += "\nAuxiliaries:"
        for auxiliary in self.auxiliaries:
            string += "\n" + auxiliary.__str__()
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

    def normalize_atoms(self, mof):
        starting_atom = next(iter(self.atoms))  # Get an atom, any atom
        visited_labels = {starting_atom.label}
        queue = deque([starting_atom])
        while queue:
            atom = queue.popleft()
            for neighbor in (n for n in atom.bondedAtoms if n in self.atoms and n.label not in visited_labels):
                d = XyzBondCreator.distance(atom, neighbor)
                if not XyzBondCreator.is_bond_distance(d, atom, neighbor):
                    for (nx, ax) in [(neighbor.a, atom.a), (neighbor.b, atom.b), (neighbor.c, atom.c)]:
                        if nx - ax > 0.5:
                            nx -= 1.0
                        elif nx - ax < -0.5:
                            nx += 1.0
                    neighbor.set_xyz_within_mof(mof)
                visited_labels.add(neighbor.label)
                queue.append(neighbor)

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
        return "({freq}x) {name}({atom_n} atom {unittype}) each bonded to {cluster} clusters, {connector} connectors, "\
               "and {aux} auxiliary groups".format(freq=self.frequency, name=atoms_string, atom_n=len(self.atoms),
                                                   unittype=unit, cluster=len(self.adjacent_cluster_ids),
                                                   connector=len(self.adjacent_connector_ids),
                                                   aux=len(self.adjacent_auxiliary_ids))

    def __eq__(self, other):
        is_isomorphic = SubGraphMatcher.are_isomorphic(self, other)
        return is_isomorphic and len(self.adjacent_connector_ids) == len(other.adjacent_connector_ids) \
            and len(self.adjacent_cluster_ids) == len(other.adjacent_cluster_ids) \
            and len(self.adjacent_auxiliary_ids) == len(other.adjacent_auxiliary_ids)
