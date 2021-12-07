from MofIdentifier.fileIO import XyzReader


class SBUDatabase:
    def __init__(self, sbu_name, file_content, MOFs, sbu_type):
        self.name = sbu_name
        self.file_content = file_content
        self.mofs = MOFs
        self.frequency = len(MOFs)
        self.type = sbu_type
        self._sbu = None

    def set_name(self, name):
        self.name = name

    def set_file_contents(self, file):
        self.file_content = file

    def set_mofs(self, mofs):
        self.mofs = mofs
        self.frequency = len(mofs)

    def get_sbu(self):
        if self._sbu is None:
            if self.file_content is not None:
                name = self.name + '.xyz'
                self._sbu = XyzReader.get_molecule_from_string(self.file_content, name)
            else:
                return None
        return self._sbu

    def get_num_atoms(self):
        atom_lines = [line.strip() for line in self.file_content.split('\n')[2:]]
        return sum(1 if len(line) > 2 else 0 for line in atom_lines)

