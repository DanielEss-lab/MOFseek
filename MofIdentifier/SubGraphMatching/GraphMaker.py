import igraph  # currently python-igraph in repositories


def graph_from_mol(molecule):
    graph = igraph.Graph()
    for atom in molecule.atoms:
        graph.add_vertex(atom.label, element=atom.type_symbol, is_bond_limited=atom.is_bond_limited)
    for atom in molecule.atoms:
        for bonded_atom in atom.bondedAtoms:
            while not bonded_atom.is_in_unit_cell():
                bonded_atom = bonded_atom.original
            if bonded_atom in molecule.atoms:
                graph.add_edge(atom.label, bonded_atom.label)
    return graph


def hydrogenless_graph_from_mol(molecule):
    graph = igraph.Graph()
    for atom in molecule.atoms:
        if atom.type_symbol != 'H':
            graph.add_vertex(atom.label, element=atom.type_symbol, is_bond_limited=atom.is_bond_limited)
    for atom in molecule.atoms:
        if atom.type_symbol != 'H':
            for bonded_atom in atom.bondedAtoms:
                if bonded_atom.type_symbol != 'H':
                    while not bonded_atom.is_in_unit_cell():
                        bonded_atom = bonded_atom.original
                    if bonded_atom in molecule.atoms:
                        graph.add_edge(atom.label, bonded_atom.label)
    return graph


def hydrogenless_graph_from_old_graph(mol):
    graph = mol.get_graph().copy()
    to_delete_ids = [v.index for v in graph.vs if 'H' == v['element']]
    graph.delete_vertices(to_delete_ids)
    return graph
