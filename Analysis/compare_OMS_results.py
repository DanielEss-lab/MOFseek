import distutils.util

import pandas as pd


def csv_to_dict(file_like):
    values = pd.read_csv(file_like, usecols=['filename', 'Has_OMS'], true_values=['Yes'], false_values=['No'],
                         skiprows=lambda x: 0 < x < 1878)
    d = values.set_index('filename').T.to_dict('list')
    answers = {k: v[0] == "Yes" for k, v in d.items()}
    return answers


if __name__ == '__main__':
    mismatches = []
    only_we = 0
    only_they = 0
    have_OMS = 0
    do_not_have_OMS = 0
    with open(r'C:\Users\mdavid4\Desktop\2019-11-01-ASR-public_12020.csv') as csv:
        control = csv_to_dict(csv)
    with open(r'C:\Users\mdavid4\Desktop\Esslab-P66\Analysis\output\open_metal_sites.csv') as file:
        has_skipped_first_line = False
        for line in file.readlines():
            if not has_skipped_first_line:
                has_skipped_first_line = True
                continue

            label_with_extension = line[0:line.index(',')]
            label = label_with_extension[0:label_with_extension.rfind('.')]
            has_OMS = not 'no open' in line
            if control[label] and has_OMS:
                have_OMS += 1
            elif has_OMS:
                only_we += 1
                mismatches.append((label, f'only we say that it has OMS'))
            elif control[label]:
                only_they += 1
                mismatches.append((label, f'only they say that it has OMS'))
            else:
                do_not_have_OMS += 1
    print(f'Number of mofs we agree have metal sites: {have_OMS}\n'
          f"Number of mofs we agree don't have metal sites: {do_not_have_OMS}\n"
          f'Number of mofs only we say have metal sites: {only_we}\n'
          f"Number of mofs only they say have metal sites: {only_they}\n"
          f'Disagreements:')
    print(*mismatches, sep="\n")
