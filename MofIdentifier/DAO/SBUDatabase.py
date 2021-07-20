from MofIdentifier.fileIO import XyzReader


class SBUDatabase:
    def __init__(self, name, file_content, mofs):
        self.name = name
        self.file_content = file_content
        self.mofs = mofs
        self.frequency = len(mofs)
        self._sbu = None

    def set_name(self, name):
        self.name = name

    def set_file_contents(self, file):
        self.file_contents = file

    def set_mofs(self, mofs):
        self.mofs = mofs
        self.frequency = len(mofs)

    def get_sbu(self):
        if self._sbu is None:
            if self.file_content is not None:
                self._sbu = XyzReader.get_molecule_from_string(self.file_content, self.name)
            else:
                return None
        return self._sbu
