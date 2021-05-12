from enum import Enum
from MofIdentifier import SubGraphMatcher


class SBUs:
    def __init__(self, clusters, connectors, auxiliaries):
        self.clusters = clusters
        self.connectors = connectors
        self.auxiliaries = auxiliaries


class UnitType(Enum):
    CLUSTER = 1
    CONNECTOR = 2
    AUXILIARY = 3


class SBU:
    def __init__(self, sbu_id, unit_type, atoms):
        self.sbu_id = sbu_id
        self.adjacent_cluster_ids = set(())
        self.adjacent_connector_ids = set(())
        self.adjacent_auxiliary_ids = set(())
        self.type = unit_type
        self.atoms = atoms
        self.frequency = 1

    def __eq__(self, other):
        is_isomorphic = SubGraphMatcher.are_isomorphic(self, other)
        return is_isomorphic and len(self.adjacent_connector_ids) == len(other.adjacent_connector_ids) \
               and len(self.adjacent_cluster_ids) == len(other.adjacent_cluster_ids) \
               and len(self.adjacent_auxiliary_ids) == len(other.adjacent_auxiliary_ids)
