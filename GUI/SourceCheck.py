from DAOsAndServices import MOFDAO
from GUI import Settings


def mof_source_is_enabled(name: str):
    source = MOFDAO.get_MOF(name).source_name
    return Settings.sources_enabled[source]
