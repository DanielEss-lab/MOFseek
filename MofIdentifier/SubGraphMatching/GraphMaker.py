import igraph


def graph_from_mol(molecule):
    graph = igraph.Graph()
    for atom in molecule.atoms:
        graph.add_vertex(atom.label, element=atom.type_symbol)
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
            graph.add_vertex(atom.label, element=atom.type_symbol)
    for atom in molecule.atoms:
        if atom.type_symbol != 'H':
            for bonded_atom in atom.bondedAtoms:
                if bonded_atom.type_symbol != 'H':
                    while not bonded_atom.is_in_unit_cell():
                        bonded_atom = bonded_atom.original
                    if bonded_atom in molecule.atoms:
                        graph.add_edge(atom.label, bonded_atom.label)
    return graph
