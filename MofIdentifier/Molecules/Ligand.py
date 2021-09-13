from MofIdentifier.Molecules import Molecule


class Ligand(Molecule.Molecule):
    def __init__(self, filepath, atoms, file_string, wildcards=None):
        self.file_content = file_string
        super().__init__(filepath, atoms)
        self.unique_wildcards = wildcards

    def __str__(self):
        return "{} ligand".format(self.label)
