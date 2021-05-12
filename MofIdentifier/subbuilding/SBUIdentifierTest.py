import unittest

from MofIdentifier import CifReader
from MofIdentifier.MofBondCreator import MofBondCreator
from MofIdentifier.XyzBondCreator import XyzBondCreator
from MofIdentifier.subbuilding import SBUIdentifier


class SBUIdentifierTest(unittest.TestCase):
    def test_simple_mof(self):
        mof_abavij = CifReader.read_mof('../ABAVIJ_clean.cif')
        bond_creator = MofBondCreator(mof_abavij)
        bond_creator.connect_atoms()
        sbu_breakdown = SBUIdentifier.split(mof_abavij)

        assert (len(sbu_breakdown.clusters) == 1)
        assert (sbu_breakdown.clusters[0].frequency == 4)
        assert (len(sbu_breakdown.clusters[0].adjacent_connector_ids) == 6)
        assert (len(sbu_breakdown.clusters[0].atoms) == 1)

        assert (len(sbu_breakdown.connectors) == 1)
        assert (sbu_breakdown.connectors[0].frequency == 8)
        assert (len(sbu_breakdown.connectors[0].adjacent_cluster_ids) == 3)
        assert (len(sbu_breakdown.connectors[0].atoms) == 13)

        assert (len(sbu_breakdown.auxiliaries) == 0)

    def test_complex_mof(self):
        mof_808 = CifReader.read_mof('../smod7-pos-1.cif')
        bond_creator = MofBondCreator(mof_808)
        bond_creator.connect_atoms()
        sbu_breakdown = SBUIdentifier.split(mof_808)

        assert (len(sbu_breakdown.clusters) == 1)
        assert (sbu_breakdown.clusters[0].frequency == 4)
        assert (len(sbu_breakdown.clusters[0].adjacent_cluster_ids) == 0)
        assert (len(sbu_breakdown.clusters[0].adjacent_connector_ids) == 6)
        assert (len(sbu_breakdown.clusters[0].adjacent_auxiliary_ids) == 10)
        assert (len(sbu_breakdown.clusters[0].atoms) == 18)

        assert (len(sbu_breakdown.connectors) == 1)
        assert (sbu_breakdown.connectors[0].frequency == 8)
        assert (len(sbu_breakdown.connectors[0].adjacent_cluster_ids) == 3)
        assert (len(sbu_breakdown.connectors[0].adjacent_connector_ids) == 0)
        assert (len(sbu_breakdown.connectors[0].adjacent_auxiliary_ids) == 0)
        assert (len(sbu_breakdown.connectors[0].atoms) == 18)

        assert (len(sbu_breakdown.auxiliaries) == 3)



if __name__ == '__main__':
    unittest.main()
