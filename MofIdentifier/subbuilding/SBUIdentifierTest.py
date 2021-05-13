import unittest

from MofIdentifier import CifReader
from MofIdentifier.MofBondCreator import MofBondCreator
from MofIdentifier.XyzBondCreator import XyzBondCreator
from MofIdentifier.subbuilding import SBUIdentifier


class SBUIdentifierTest(unittest.TestCase):
    def test_simple_mof(self):
        mof_abavij = CifReader.read_mof('../mofsForTests/ABAVIJ_clean.cif')
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
        mof_808 = CifReader.read_mof('../mofsForTests/smod7-pos-1.cif')
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

    def test_small_mof(self):
        mof_abetae = CifReader.read_mof('../mofsForTests/ABETAE_clean.cif')
        bond_creator = MofBondCreator(mof_abetae)
        bond_creator.connect_atoms()
        sbu_breakdown = SBUIdentifier.split(mof_abetae)

        assert (len(sbu_breakdown.clusters) == 1)
        assert (sbu_breakdown.clusters[0].frequency == 20)
        assert (len(sbu_breakdown.clusters[0].adjacent_cluster_ids) == 0)
        assert (len(sbu_breakdown.clusters[0].adjacent_connector_ids) == 4)
        assert (len(sbu_breakdown.clusters[0].adjacent_auxiliary_ids) == 0)
        assert (len(sbu_breakdown.clusters[0].atoms) == 1)

        assert (len(sbu_breakdown.connectors) == 1)
        assert (sbu_breakdown.connectors[0].frequency == 16)
        assert (len(sbu_breakdown.connectors[0].adjacent_cluster_ids) == 5)
        assert (len(sbu_breakdown.connectors[0].adjacent_connector_ids) == 0)
        assert (len(sbu_breakdown.connectors[0].adjacent_auxiliary_ids) == 0)
        assert (len(sbu_breakdown.connectors[0].atoms) == 5)

    def test_notalladjacent_core(self):
        mof_akoheo = CifReader.read_mof('../mofsForTests/AKOHEO_clean.cif')
        bond_creator = MofBondCreator(mof_akoheo)
        bond_creator.connect_atoms()
        sbu_breakdown = SBUIdentifier.split(mof_akoheo)

        assert (len(sbu_breakdown.clusters) == 2)
        iron_node = None
        big_node = None
        for cluster in sbu_breakdown.clusters:
            if len(cluster.atoms) == 1:
                iron_node = cluster
            elif len(cluster.atoms) == 31:
                big_node = cluster
        assert (iron_node is not None and big_node is not None)
        assert (iron_node.frequency == 4)
        assert (big_node.frequency == 2)
        assert (len(iron_node.adjacent_cluster_ids) == len(big_node.adjacent_cluster_ids) == 0)
        assert (len(iron_node.adjacent_connector_ids) == 5)
        assert (len(iron_node.adjacent_auxiliary_ids) == 1)
        assert (len(big_node.adjacent_connector_ids) == 8)
        assert (len(big_node.adjacent_auxiliary_ids) == 0)

        assert (len(sbu_breakdown.connectors) == 1)
        assert (sbu_breakdown.connectors[0].frequency == 16)
        assert (len(sbu_breakdown.connectors[0].adjacent_cluster_ids) == 3)
        assert (len(sbu_breakdown.connectors[0].adjacent_connector_ids) == 0)
        assert (len(sbu_breakdown.connectors[0].adjacent_auxiliary_ids) == 0)
        assert (len(sbu_breakdown.connectors[0].atoms) == 5)

        assert (len(sbu_breakdown.auxiliaries) == 1)
        assert (sbu_breakdown.auxiliaries[0].frequency == 4)
        assert (len(sbu_breakdown.auxiliaries[0].adjacent_cluster_ids) == 1)
        assert (len(sbu_breakdown.auxiliaries[0].adjacent_connector_ids) == 0)
        assert (len(sbu_breakdown.auxiliaries[0].adjacent_auxiliary_ids) == 0)
        assert (len(sbu_breakdown.auxiliaries[0].atoms) == 2)



if __name__ == '__main__':
    unittest.main()
