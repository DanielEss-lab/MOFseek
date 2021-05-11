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
        self.adjacent_sbu_ids = set(())
        self.type = unit_type
        self.atoms = atoms
        self.frequency = 0

    def __eq__(self, other):
        is_isomorphic = SubGraphMatcher.are_isomorphic(self, other)
        return is_isomorphic and len(self.adjacent_sbu_ids) == len(other.adjacent_sbu_ids)
