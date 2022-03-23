from collections import namedtuple

from DAOsAndServices import SBUDAO
from MofIdentifier.fileIO import MoleculeWriter


def export_all_sbus():
    MoleculeLike = namedtuple('MoleculeLike', ['label', 'file_content'])
    for sbu in SBUDAO.get_sbu_iterator():
        date = "3_22_2022"
        if sbu.type == 'cluster':
            path = fr'C:\Users\mdavid4\Downloads\{date}_sbus\nodes'
        elif sbu.type == 'connector':
            path = fr'C:\Users\mdavid4\Downloads\{date}_sbus\connectors'
        elif sbu.type == 'auxiliary':
            path = fr'C:\Users\mdavid4\Downloads\{date}_sbus\auxiliaries'
        else:
            raise ValueError('SBU type must be one of: cluster, connector, auxiliary')
        MoleculeWriter.write_one(MoleculeLike(sbu.name + '.xyz', sbu.file_content), path)


if __name__ == '__main__':
    export_all_sbus()
