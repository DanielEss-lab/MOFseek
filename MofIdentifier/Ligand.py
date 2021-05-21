class Ligand:
    def __init__(self, label, atoms):
        slice_index = label.rfind('\\')
        if slice_index > -1:
            self.label = label[slice_index + 1:]
        else:
            self.label = label
        self.atoms = atoms
        self.should_use_weak_comparison = False
        self.elementsPresent = set()
        for atom in atoms:
            self.elementsPresent.add(atom.type_symbol)

    def __str__(self):
        return "{} ligand".format(self.label)
