from MofIdentifier.fileIO import LigandReader


class LigandDatabase:
    def __init__(self, ligand_name, ligand_file, Mofs):
        self.name = ligand_name
        self.file_content = ligand_file
        self.Mofs = Mofs
        self._ligand = None

    def get_ligand(self):
        if self._ligand is None:
            if self.file_content is not None:
                if len(self.file_content.split('\n')) > 2:
                    name = self.name + '.xyz'
                else:
                    name = self.name + '.smiles'
                self._ligand = LigandReader.get_mol_from_string(self.file_content, name)
            else:
                return None
        return self._ligand

    @classmethod
    def from_dict(cls, ligand_obj):
        return cls(ligand_obj["ligand_name"], ligand_obj["ligand_file_content"], ligand_obj["MOFs"])
