from MofIdentifier.SubGraphMatching import SubGraphMatcher


class Molecule:
    def __init__(self, label, atoms, igraph=None, weak_comparison_enabled=False):
        slice_index = label.rfind('\\')
        if slice_index > -1:
            self.label = label[slice_index + 1:]
        else:
            self.label = label
        self.atoms = atoms
        self.elementsPresent = set()
        self.igraph = igraph
        self.should_use_weak_comparison = weak_comparison_enabled

    def get_graph(self):
        if self.igraph is None:
            self.igraph = SubGraphMatcher.graph_from_mol(self)
        return self.igraph
