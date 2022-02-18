import cProfile
from MofIdentifier.fileIO import CifReader


def read_mofs():
    mofs = CifReader.get_all_mofs_in_directory(r'C:\Users\mdavid4\Desktop\Esslab-P66\MofIdentifier\mofsForTests')
    sbus = [mof.sbus() for mof in mofs]


if __name__ == '__main__':
    cProfile.run('read_mofs()')
