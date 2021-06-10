from collections import deque
from enum import Enum

from MofIdentifier.Molecules import Molecule
from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.bondTools import Distances


class SBUCollection:
    def __init__(self, clusters, connectors, auxiliaries):
        self.clusters = clusters
        self.num_cluster_atoms = sum(len(sbu.atoms) * sbu.frequency for sbu in clusters)
        self.connectors = connectors
        self.num_connector_atoms = sum(len(sbu.atoms) * sbu.frequency for sbu in connectors)
        self.auxiliaries = auxiliaries
        self.num_auxiliary_atoms = sum(len(sbu.atoms) * sbu.frequency for sbu in auxiliaries)
        self.avg_node_connectivity = sum(len(sbu.adjacent_connector_ids) * sbu.frequency for sbu in clusters) / \
            sum(sbu.frequency for sbu in clusters)
        self.avg_conn_connectivity = sum(len(sbu.adjacent_cluster_ids) * sbu.frequency for sbu in connectors) / \
            sum(sbu.frequency for sbu in connectors)

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

    def all(self):
        return self.clusters + self.connectors + self.auxiliaries

    def __add__(self, other):
        return SBUCollection(self.clusters + other.clusters, self.connectors
                             + other.connectors, self.auxiliaries + other.auxiliaries)

    @classmethod
    def from_tuples(cls, tuples):
        clusters, connectors, auxiliaries = [], [], []
        for tuple in tuples:
            clusters.extend(tuple[0])
            connectors.extend(tuple[1])
            auxiliaries.extend(tuple[2])
        return SBUCollection(clusters, connectors, auxiliaries)

class UnitType(Enum):
    CLUSTER = 1
    CONNECTOR = 2
    AUXILIARY = 3

    def __str__(self):
        return "cluster" if self == UnitType.CLUSTER else "connector" if self == UnitType.CONNECTOR else "auxiliary"


class SBU(Molecule.Molecule):
    def __init__(self, sbu_id, unit_type, atoms):
        super().__init__('No Filepath/Unlabeled', atoms)
        self.sbu_id = sbu_id
        self.adjacent_cluster_ids = set(())
        self.adjacent_connector_ids = set(())
        self.adjacent_auxiliary_ids = set(())
        self.type = unit_type
        self.frequency = 1

    def connections(self):
        return len(self.adjacent_auxiliary_ids) + len(self.adjacent_cluster_ids) + len(self.adjacent_connector_ids)

    def add_atom(self, atom):
        self.atoms.add(atom)
        self.elementsPresent.add(atom.type_symbol)

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
                d = Distances.distance(atom, neighbor)
                if not Distances.is_bond_distance(d, atom, neighbor):
                    da = db = dc = 0
                    if neighbor.a - atom.a > 0.5:
                        da -= 1.0
                    elif neighbor.a - atom.a < -0.5:
                        da += 1.0
                    if neighbor.b - atom.b > 0.5:
                        db -= 1.0
                    elif neighbor.b - atom.b < -0.5:
                        db += 1.0
                    if neighbor.c - atom.c > 0.5:
                        dc -= 1.0
                    elif neighbor.c - atom.c < -0.5:
                        dc += 1.0
                    neighbor_in_right_place = neighbor.copy_to_relative_position(da, db, dc, mof.angles,
                                                                                 mof.fractional_lengths)
                else:
                    neighbor_in_right_place = neighbor
                visited.add(neighbor_in_right_place)
                queue.append(neighbor_in_right_place)
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
        if isinstance(other, SBU):
            return is_isomorphic and len(self.adjacent_connector_ids) == len(other.adjacent_connector_ids) \
                and len(self.adjacent_cluster_ids) == len(other.adjacent_cluster_ids) \
                and len(self.adjacent_auxiliary_ids) == len(other.adjacent_auxiliary_ids)
        else:
            return is_isomorphic

    def graph_equals(self, other):
        return len(self.atoms) == len(other.atoms) and SubGraphMatcher.match(self, other)
