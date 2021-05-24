import time

from MofIdentifier.SubGraphMatching import SubGraphMatcher, GraphMaker
from MofIdentifier.fileIO import LigandReader


if __name__ == '__main__':
    # uses https://pypi.org/project/PyCifRW/4.3/#description to read CIF files

    molecule = LigandReader.get_mol_from_file('ligands/Periodic_55_conn_some_bonds.xyz')
    molecule.get_graph()
    start_time = time.time()
    for i in range(1000):
        from_scratch = GraphMaker.hydrogenless_graph_from_mol(molecule)
    between_time = time.time()
    for i in range(1000):
        from_graph = GraphMaker.hydrogenless_graph_from_old_graph(molecule)
    end_time = time.time()
    assert(len(from_graph.vs) == len(from_scratch.vs))
    assert (len(from_graph.es) == len(from_scratch.es))
    print("From Scratch took", between_time - start_time)
    print("From graph took", end_time - between_time)
