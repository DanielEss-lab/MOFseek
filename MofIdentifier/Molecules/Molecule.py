from MofIdentifier.SubGraphMatching import GraphMaker


class Molecule:
    def __init__(self, label, atoms, igraph=None, weak_comparison_enabled=False):
        slice_index = max(label.rfind('\\'), label.rfind('/'))
        if slice_index > -1:
            self.label = label[slice_index + 1:]
        else:
            self.label = label
        self.atoms = atoms
        self.elementsPresent = set()
        self.graph = igraph
        self.no_h_graph = None
        self.should_use_weak_comparison = weak_comparison_enabled

    def get_graph(self):
        if self.should_use_weak_comparison:
            return self.get_hydrogenless_graph()
        else:
            if self.graph is None:
                self.graph = GraphMaker.graph_from_mol(self)
            return self.graph

    def get_hydrogenless_graph(self):
        if self.no_h_graph is None:
            if 'H' not in self.elementsPresent:
                self.no_h_graph = self.graph
            elif self.graph is None:
                self.no_h_graph = GraphMaker.hydrogenless_graph_from_mol(self)
            else:
                self.no_h_graph = GraphMaker.hydrogenless_graph_from_old_graph(self)
        return self.no_h_graph
