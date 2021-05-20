from pysmiles import read_smiles

from MofIdentifier.Ligand import Ligand
from MofIdentifier.atom import Atom


def mol_from_file(filepath):
    with open(filepath, 'r') as file:
        line = file.readline()
    return mol_from_str(line, filepath)


def mol_from_str(string, mol_name=None):
    if mol_name is None:
        mol_name = string
    manually_specified_h = 'H' in string
    networkx_mol = read_smiles(string, explicit_hydrogen=not manually_specified_h)
    networkx_nodes = list(networkx_mol.nodes(data='element'))
    atoms = {}
    for node in networkx_nodes:
        name = str(node[1]) + str(node[0])
        atoms[name] = Atom(str(name), str(node[1]), float('inf'), float('inf'), float('inf'))
    for node in networkx_nodes:
        name = str(node[1]) + str(node[0])
        atom = atoms[name]
        for adj_node in list(networkx_mol.adj[node[0]]):
            adj = networkx_nodes[adj_node]
            adj_name = str(adj[1]) + str(adj[0])
            atom.bondedAtoms.append(atoms[adj_name])
    molecule = Ligand(mol_name, list(atoms.values()))
    molecule.should_use_weak_comparison = not manually_specified_h
    return molecule


if __name__ == '__main__':
    mol = mol_from_str('C1=NNN=N1')
    print(mol)
    print(*mol.atoms, sep='\n')
