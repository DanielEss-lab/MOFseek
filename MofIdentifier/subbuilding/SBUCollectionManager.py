import glob
import os

from MofIdentifier import SubGraphMatcher
from MofIdentifier.fileIO import XyzReader, XyzWriter
from MofIdentifier.subbuilding import SBUTools
from MofIdentifier.subbuilding.SBUTools import UnitType


def add_new_sbus_to_collection(sbus):
    existing_sbus = get_existing_sbus()
    new_sbus = filter_for_new_sbus(existing_sbus, sbus)
    write_sbus(new_sbus, {UnitType.CLUSTER: len(new_sbus.clusters),
                          UnitType.CONNECTOR: len(new_sbus.connectors),
                          UnitType.AUXILIARY: len(new_sbus.auxiliaries)})


def get_existing_sbus():
    clusters = []
    connectors = []
    aux = []
    for filename in glob.glob(os.path.join('/cluster', '*.xyz')):
        clusters.append(XyzReader.get_molecule(filename))
    for filename in glob.glob(os.path.join('/connector', '*.xyz')):
        connectors.append(XyzReader.get_molecule(filename))
    for filename in glob.glob(os.path.join('/auxiliary', '*.xyz')):
        aux.append(XyzReader.get_molecule(filename))
    return SBUTools.SBUs(clusters, connectors, aux)


def filter_for_new_sbus(existing_sbus, sbus_in_question):
    new_clusters = SubGraphMatcher.filter_for_molecules_not_in_set(sbus_in_question.clusters, existing_sbus.clusters)
    new_conn = SubGraphMatcher.filter_for_molecules_not_in_set(sbus_in_question.connectors, existing_sbus.connectors)
    new_aux = SubGraphMatcher.filter_for_molecules_not_in_set(sbus_in_question.auxiliaries, existing_sbus.auxiliaries)
    return SBUTools.SBUs(new_clusters, new_conn, new_aux)


def write_sbus(new_sbus, file_counts):
    def write_some_sbus(sbus, type_name, num_type):
        for sbu in sbus:
            XyzWriter.write_molecule_to_file(type_name + '_' + str(num_type), sbu.atoms)
            num_type += 1
    write_some_sbus(new_sbus.clusters, str(UnitType.CLUSTER), file_counts[UnitType.CLUSTER])
    write_some_sbus(new_sbus.connectors, str(UnitType.CONNECTOR), file_counts[UnitType.CONNECTOR])
    write_some_sbus(new_sbus.auxiliaries, str(UnitType.AUXILIARY), file_counts[UnitType.AUXILIARY])

