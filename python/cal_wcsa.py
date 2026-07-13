import csv
import sys
from pathlib import Path

import adif_io

from awards.wcsa import compute_wcsa, load_school_list


CSV_HEADER = [
    'School Call',
    'School Name',
    'Date',
    'Time',
    'Band',
    'Mode',
    'Prop Mode',
    'Satellite',
    'Callsign',
]


def main():
    if len(sys.argv) >= 2:
        adif_file = sys.argv[1]
    else:
        adif_file = input("Your ADIF File: ").strip('\'"')

    schools = load_school_list(get_school_list_path())
    qsos, header = adif_io.read_from_file(adif_file)
    result = compute_wcsa(qsos, schools)

    print_result(result)
    write_checksheet('wcsa_checksheet.csv', result)


def get_school_list_path():
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / 'data' / 'wcsa.json'

    root_dir = Path(__file__).resolve().parents[1]
    return root_dir / 'data' / 'wcsa.json'


def print_result(result):
    print("----------WCSA AWARD STATUS----------")
    print("Schools: %d" % result['SCHOOL_COUNT'])
    print("Slots:   %d" % result['SLOT_COUNT'])
    print("-------------------------------------")

    for level in result['LEVELS']:
        status = "OK" if level['ACHIEVED'] else ""
        print(
            "%-6s  %-2s  schools %2d / %d  slots %2d / %d" % (
                level['NAME'],
                status,
                result['SCHOOL_COUNT'],
                level['REQUIRED_SCHOOLS'],
                result['SLOT_COUNT'],
                level['REQUIRED_SLOTS'],
            )
        )

    print("-------------------------------------")
    print("School slots:")
    for school_call, count in result['SLOT_COUNTS_BY_SCHOOL'].items():
        slot = next(s for s in result['SLOTS'].values() if s['SCHOOL_CALL'] == school_call)
        print("%-10s  %-4d  %s" % (school_call, count, slot['SCHOOL_NAME']))
    print("-------------------------------------")


def write_checksheet(csv_file, result):
    rows = sorted(
        result['SLOTS'].values(),
        key=lambda slot: (
            slot['SCHOOL_CALL'],
            slot['QSO'].get('QSO_DATE', ''),
            slot['QSO'].get('TIME_ON', ''),
            slot['QSO'].get('BAND', ''),
            slot['QSO'].get('MODE', ''),
            slot['QSO'].get('PROP_MODE', ''),
            slot['QSO'].get('SAT_NAME', ''),
        ),
    )

    with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
        csv_writer = csv.writer(f, dialect='excel')
        csv_writer.writerow(CSV_HEADER)
        for slot in rows:
            qso = slot['QSO']
            csv_writer.writerow([
                slot['SCHOOL_CALL'],
                slot['SCHOOL_NAME'],
                qso.get('QSO_DATE', ''),
                qso.get('TIME_ON', ''),
                qso.get('BAND', ''),
                qso.get('MODE', ''),
                qso.get('PROP_MODE', ''),
                qso.get('SAT_NAME', ''),
                qso.get('CALL', ''),
            ])


if __name__ == '__main__':
    main()
