class Ligand:
    def __init__(self, label, atoms):
        self.label = label
        self.atoms = atoms
        self.elementsPresent = set()
        for atom in atoms:
            self.elementsPresent.add(atom.type_symbol)

    def __str__(self):
        return "{} ligand".format(self.label)
