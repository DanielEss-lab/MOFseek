from matplotlib import pyplot as plt

from DAO import MOFDAO


def create_histogram(xlabel, values, num_bins):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.hist(values, bins=num_bins)
    ax.set(xlabel=xlabel, ylabel='num of MOFs')
    # ax.grid()


def chart(xlabel, get_value, num_bins=20):
    values = [get_value(mof) for mof in MOFDAO.get_mof_iterator() if get_value(mof) is not None]
    create_histogram(xlabel, values, num_bins)


if __name__ == '__main__':
    chart('Largest Cavity Diameter', lambda mof: mof.LCD, 90)
    chart('Pore Limiting Diameter', lambda mof: mof.PLD, 90)
    chart('Largest sphere along the Free Path Diameter', lambda mof: mof.LFPD, 90)
    chart('Accessible Surface Area (m2 cm3)', lambda mof: mof.ASA_m2_cm3, 30)
    chart('Accessible Surface Area (m2 g)', lambda mof: mof.ASA_m2_g, 30)
    chart('Non-Accessible Surface Area (m2 cm3)', lambda mof: mof.NASA_m2_cm3, 30)
    chart('Non-Accessible Surface Area (m2 g)', lambda mof: mof.NASA_m2_g, 30)
    chart('Void Fraction', lambda mof: mof.AV_VF, 40)

    """
    "ASA_m2_cm3": Attribute("Accessible Surface Area", lambda mof: round(mof.ASA_m2_cm3, 3) if mof.ASA_m2_cm3 is not None else None, False, float),
    "ASA_m2_g": Attribute("Accessible Surface Area", lambda mof: round(mof.ASA_m2_g, 3) if mof.ASA_m2_g is not None else None, False, float),
    "NASA_m2_cm3": Attribute("Non-Accessible Surface Area", lambda mof: round(mof.NASA_m2_cm3, 3) if mof.NASA_m2_cm3 is not None else None, False, float),
    "NASA_m2_g": Attribute("Non-Accessible Surface Area", lambda mof: round(mof.NASA_m2_g, 3) if mof.NASA_m2_g is not None else None, False, float),
    "AV_VF": Attribute("Void Fraction, 0-1", lambda mof: round(mof.AV_VF, 3) if mof.AV_VF is not None else None, False, float),
    "NAV_cm3_g": Attribute("Non-Accessible Volume", lambda mof: round(mof.NAV_cm3_g, 7) if mof.NAV_cm3_g is not None else None, False, float),
    """
    plt.show()
