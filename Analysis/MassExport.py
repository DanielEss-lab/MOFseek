from collections import namedtuple

from DAO import SBUDAO
from MofIdentifier.fileIO import MoleculeWriter


def export_all_sbus():
    MoleculeLike = namedtuple('MoleculeLike', ['label', 'file_content'])
    for sbu in SBUDAO.get_sbu_iterator():
        if sbu.type == 'cluster':
            path = r'C:\Users\mdavid4\Downloads\sbus\nodes'
        elif sbu.type == 'connector':
            path = r'C:\Users\mdavid4\Downloads\sbus\connectors'
        elif sbu.type == 'auxiliary':
            path = r'C:\Users\mdavid4\Downloads\sbus\auxiliaries'
        else:
            raise ValueError('SBU type must be one of: cluster, connector, auxiliary')
        MoleculeWriter.write_one(MoleculeLike(sbu.name + '.xyz', sbu.file_content), path)


if __name__ == '__main__':
    export_all_sbus()
