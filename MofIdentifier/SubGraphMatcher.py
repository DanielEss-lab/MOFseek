from MofIdentifier import WeakSubGraphMatcher, StrongSubGraphMatcher


def graph_from_mol(mol1):
    if mol1.should_use_weak_comparison:
        graph1 = WeakSubGraphMatcher.igraph_from_molecule(mol1)
    else:
        graph1 = StrongSubGraphMatcher.igraph_from_molecule(mol1)
    return graph1


def match(mol1, mol2):
    graph1 = graph_from_mol(mol1)
    graph2 = graph_from_mol(mol2)
    if mol1.should_use_weak_comparison or mol2.should_use_weak_comparison:
        return WeakSubGraphMatcher.graphs_near_isomorphic(graph1, graph2)
    else:
        return StrongSubGraphMatcher.graphs_are_isomorphic(graph1, graph2)


def find_ligand_in_mof(ligand, mof):
    lGraph = graph_from_mol(ligand)
    if len(lGraph.clusters()) != 1:
        raise Exception('Every atom in the ligand must be connected to a single molecule; try tweaking the input file '
                        'and try again.')
    mGraph = StrongSubGraphMatcher.igraph_from_molecule(mof)
    mof_contains_ligand = mGraph.subisomorphic_vf2(lGraph, node_compat_fn=StrongSubGraphMatcher.vertices_are_equal)
    return mof_contains_ligand

