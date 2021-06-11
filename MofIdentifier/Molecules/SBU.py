from MofIdentifier.Molecules import Molecule
from MofIdentifier.SubGraphMatching import SubGraphMatcher


class SBU(Molecule.Molecule):
    def __init__(self, changeable_sbu):
        super().__init__(changeable_sbu.filepath, list(changeable_sbu.atoms))
        self.adjacent_cluster_ids = changeable_sbu.adjacent_cluster_ids
        self.adjacent_connector_ids = changeable_sbu.adjacent_connector_ids
        self.adjacent_auxiliary_ids = changeable_sbu.adjacent_auxiliary_ids
        self.type = changeable_sbu.type
        self.frequency = changeable_sbu.frequency

    def connections(self):
        return len(self.adjacent_auxiliary_ids) + len(self.adjacent_cluster_ids) + len(self.adjacent_connector_ids)

    def __str__(self):
        return "{freq}x {label}: {atoms}({atom_n} atom {unittype}) each bonded to {cluster} clusters, {connector} " \
               "connectors, and {aux} auxiliary groups".format(label=self.label, freq=self.frequency,
                                                               atoms=self.atoms_string(), atom_n=len(self.atoms),
                                                               unittype=str(self.type),
                                                               cluster=len(self.adjacent_cluster_ids),
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