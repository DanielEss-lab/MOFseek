from MofIdentifier.Molecules import Molecule


class Ligand(Molecule.Molecule):
    def __init__(self, filepath, atoms, file_string, wildcards=None):
        self.file_content = file_string
        super().__init__(filepath, atoms)
        self.unique_wildcards = wildcards if wildcards is not None else dict()

    def __str__(self):
        return "{} ligand".format(self.label)

    def concrete_elements_present(self):
        elements = set(self.elementsPresent.keys())
        for element in self.elementsPresent:
            if (element == wc.symbol for wc in self.unique_wildcards) or element in '#%*':
                elements.remove(element)
        return elements
