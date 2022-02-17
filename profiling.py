import cProfile
from MofIdentifier.fileIO import CifReader


def read_mofs():
    CifReader.get_all_mofs_in_directory(r'C:\Users\mdavid4\Desktop\Esslab-P66\MofIdentifier\mofsForTests')


if __name__ == '__main__':
    cProfile.run('read_mofs()')
