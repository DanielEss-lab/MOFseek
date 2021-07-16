import glob
import os
from pathlib import Path

from MofIdentifier.Molecules import SBU
from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.fileIO import XyzReader, XyzWriter, CifReader, LigandReader
from MofIdentifier.subbuilding import SBUIdentifier
from MofIdentifier.subbuilding.SBUTools import UnitType, SBUCollection


def process_new_mof(mof):
    existing_sbus = get_existing_sbus()
    (new_sbus, recognized_sbus) = match_to_existing_sbus(existing_sbus, mof.sbus())
    write_sbus(new_sbus, {UnitType.CLUSTER: len(existing_sbus[0]),
                          UnitType.CONNECTOR: len(existing_sbus[1]),
                          UnitType.AUXILIARY: len(existing_sbus[2])})
    clusters = [SBU.SBU(sbu) for sbu in new_sbus[0] + recognized_sbus[0]]
    connectors = [SBU.SBU(sbu) for sbu in new_sbus[1] + recognized_sbus[1]]
    aux = [SBU.SBU(sbu) for sbu in new_sbus[2] + recognized_sbus[2]]
    return SBUCollection(clusters, connectors, aux)


def get_existing_sbus():  # NOTE: right now this just returns a SBUCollection of Ligand objects, not sbus
    clusters = []
    connectors = []
    aux = []
    for filename in glob.glob(os.path.join(Path(__file__).parent / 'cluster/', '*.xyz')):
        clusters.append(XyzReader.get_molecule(filename))
    for filename in glob.glob(os.path.join(Path(__file__).parent / 'connector/', '*.xyz')):
        connectors.append(XyzReader.get_molecule(filename))
    for filename in glob.glob(os.path.join(Path(__file__).parent / 'auxiliary/', '*.xyz')):
        aux.append(XyzReader.get_molecule(filename))
    return (clusters, connectors, aux)


def match_to_existing_sbus(existing_sbus, sbus_in_question):
    new_clusters, found_clusters = \
        SubGraphMatcher.name_molecules_from_set(sbus_in_question.clusters, existing_sbus[0])
    new_conn, found_conn = \
        SubGraphMatcher.name_molecules_from_set(sbus_in_question.connectors, existing_sbus[1])
    new_aux, found_aux = \
        SubGraphMatcher.name_molecules_from_set(sbus_in_question.auxiliaries, existing_sbus[2])
    return (new_clusters, new_conn, new_aux), (found_clusters, found_conn, found_aux)


def write_sbus(new_sbus, file_counts):
    def write_some_sbus(sbus, type_name, num_type):
        sbus_to_write = SBUIdentifier.reduce_duplicates(sbus, lambda x, y: x.graph_equals(y))
        for sbu in sbus_to_write:
            file_name = type_name + '_' + str(num_type)  # TODO: fix so that it never overwrites files (even after deleting a file)
            sbu.label = file_name
            file_path = os.path.join(Path(__file__).parent, type_name, file_name + '.xyz')
            sbu.filepath = file_path
            XyzWriter.write_molecule_to_file(file_path, sbu, file_name)
            num_type += 1
        if len(sbus) != len(sbus_to_write):
            share_names(sbus)
    write_some_sbus(new_sbus[0], str(UnitType.CLUSTER), file_counts[UnitType.CLUSTER])
    write_some_sbus(new_sbus[1], str(UnitType.CONNECTOR), file_counts[UnitType.CONNECTOR])
    write_some_sbus(new_sbus[2], str(UnitType.AUXILIARY), file_counts[UnitType.AUXILIARY])


def share_names(sbu_list):
    i = 0
    while i < len(sbu_list):
        j = i + 1
        while j < len(sbu_list):
            if sbu_list[i].label == 'Unlabeled':
                if sbu_list[i].graph_equals(sbu_list[j]):
                    sbu_list[i].label = sbu_list[j].label
                    sbu_list[i].filepath = sbu_list[j].filepath
            elif sbu_list[j].label == 'Unlabeled':
                if sbu_list[j].graph_equals(sbu_list[i]):
                    sbu_list[j].label = sbu_list[i].label
                    sbu_list[j].filepath = sbu_list[i].filepath
            j += 1
        i += 1


def read_sbus_from_files(sbu_names):
    sbus = []
    sbus_found = 0
    for kind in ["cluster", "connector", "auxiliary"]:
        for file_name_in_directory in os.listdir(Path(__file__).parent / kind):
            if file_name_in_directory.endswith(".xyz") or file_name_in_directory.endswith(".smiles"):
                for l_name in sbu_names:
                    if file_name_in_directory == l_name:
                        sbus.append(
                            LigandReader.get_mol_from_file(str(Path(__file__).parent / kind / l_name)))
                        sbus_found += 1
    if sbus_found < len(sbu_names):
        raise FileNotFoundError('Did not find all sbus')
    return sbus


if __name__ == '__main__':
    mof = CifReader.get_mof('../../GUI/mofsForGui_temp/acscombsci.5b00188_24205_clean.cif')
    sbus = process_new_mof(mof)
    print(mof.label)
    print(sbus)