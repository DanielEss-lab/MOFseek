from DAOsAndServices import MOFDAO
from DAOsAndServices.SBUDatabase import SBUDatabase
from GUI import Settings


def mof_source_is_enabled(name: str):
    source = MOFDAO.get_MOF(name).source_name
    return Settings.current_source_states()[source]


def enabled_mofs_of_sbu(sbu: SBUDatabase):
    return (name for name in sbu.mofs if mof_source_is_enabled(name))

