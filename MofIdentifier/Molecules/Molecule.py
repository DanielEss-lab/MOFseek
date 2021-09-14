from MofIdentifier.SubGraphMatching import GraphMaker


class Molecule:
    def __init__(self, filepath, atoms, igraph=None, weak_comparison_enabled=False):
        self.unique_wildcards = None
        self.filepath = filepath
        slice_index = max(filepath.rfind('\\'), filepath.rfind('/'))
        if slice_index > -1:
            self.label = filepath[slice_index + 1:]
        else:
            self.label = filepath
        self.atoms = atoms
        self.elementsPresent = dict()
        for atom in atoms:
            if atom.type_symbol in self.elementsPresent:
                self.elementsPresent[atom.type_symbol] += 1
            else:
                self.elementsPresent[atom.type_symbol] = 1
        self.graph = igraph
        self.no_h_graph = None
        self.should_use_weak_comparison = weak_comparison_enabled

    def __str__(self):
        return self.atoms_string()

    def atoms_string(self):
        string = ''
        elements = list(self.elementsPresent)
        elements.sort()
        for element in elements:
            string = string + str(self.elementsPresent[element]) + ' ' + element + ',  '
        return string[0:-3]

    def get_graph(self):
        if self.should_use_weak_comparison:
            return self.get_hydrogenless_graph()
        else:
            if self.graph is None:
                self.graph = GraphMaker.graph_from_mol(self)
            return self.graph

    def get_hydrogenless_graph(self):
        if self.no_h_graph is None:
            if self.graph is None:
                self.no_h_graph = GraphMaker.hydrogenless_graph_from_mol(self)
            elif 'H' not in self.elementsPresent:
                self.no_h_graph = self.graph
            else:
                self.no_h_graph = GraphMaker.hydrogenless_graph_from_old_graph(self)
        return self.no_h_graph
