from itertools import chain

import networkx as nx
from pysmiles import write_smiles


def _make_networkx_mol(sbuDB):  # Does not work on MOFs or crystalline structures
    sbu = sbuDB.get_sbu()
    g = nx.Graph()
    g.add_nodes_from((atom.label, {"element": atom.type_symbol}) for atom in sbu.atoms)
    g.add_edges_from(list(chain.from_iterable((((atom.label, bonded_atom.label) for bonded_atom in atom.bondedAtoms) for atom in sbu.atoms))))
    return g


def _make_smiles(networkx_mol):
    sm_str = write_smiles(networkx_mol)
    return sm_str


def get_smiles(sbuDB):
    return _make_smiles(_make_networkx_mol(sbuDB))
