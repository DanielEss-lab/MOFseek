import sys

from MofIdentifier.fileIO import CifReader, XyzWriter
from MofIdentifier.subbuilding import SBUIdentifier


def extract_cluster(input_cif_file_path, output_xyz_file_path):
    mof = CifReader.get_mof(input_cif_file_path)
    clusters = SBUIdentifier.split(mof, True).nodes_with_auxiliaries()
    clusters = [cluster for cluster in clusters if len(cluster[0].atoms) > 1]
    cluster = clusters[0]
    atoms = cluster[0].atoms
    for aux in cluster[1]:
        atoms.update(aux.atoms)
    file_content = XyzWriter.atoms_to_xyz_string(atoms, "generated cluster")
    with open(output_xyz_file_path, "w") as f:
        f.write(file_content)


if __name__ == '__main__':
    if len(sys.argv) == 3:
        extract_cluster(sys.argv[1], sys.argv[2])
    else:
        print('Error: Incorrect calling of main method.\nUsage: python main input_cif_file_path output_xyz_file_path')
