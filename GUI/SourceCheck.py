from DAOsAndServices import MOFDAO
from GUI import Settings


def mof_source_is_enabled(name: str):
    return any(Settings.current_source_states()[source] for source in MOFDAO.get_MOF(name).source_names)


def enabled_mofs_of_sbu(sbu):  # SBUDatabase
    return (name for name in sbu.mofs if mof_source_is_enabled(name))
