import sys
import os
from os import path
import adif_io
import csv
import json
from collections import defaultdict


path_to_no_list = path.abspath(path.join(path.dirname(__file__), 'no_list.json'))
path_to_pref_list   = path.abspath(path.join(path.dirname(__file__), 'pref_list.json'))

with open(path_to_no_list, "r", encoding="utf-8") as f:
    no_list = json.load(f)

with open(path_to_pref_list, "r", encoding="utf-8") as f:
    pref_list = json.load(f)

def get_district(no):
    id = int(no)
    if id == 1:
        return '8'
    elif id >= 2 and id <= 7:
        return '7'
    elif id >= 8 and id <= 9:
        return '0'
    elif id >= 10 and id <= 17:
        return '1'
    elif id >= 18 and id <= 21:
        return '2'
    elif id >= 22 and id <= 27:
        return '3'
    elif id >= 28 and id <= 30:
        return '9'
    elif id >= 31 and id <= 35:
        return '4'
    elif id >= 36 and id <= 39:
        return '5'
    elif id >= 40 and id <= 47:
        return '6'

def get_pref_name(no):
    if no in pref_list:
        return pref_list[no]['kanji']
    return 'ERROR'


def gun_name_with_suffix(name):
    if ' (' in name:
        return name.replace(' (', '郡 (')
    elif '支庁' in name:
        return name
    else:
        return name + '郡'


def get_no_name_list(no):
    if no not in no_list:
        return []
    
    origin_name = no_list[no]['ja_name']
    name = [
        get_pref_name(no[0:2]),
    ]

    if len(no) == 4:  # city
        if no == '1001':    # Tokyo 23 wards
            name = [origin_name]
        else:
            name.append(origin_name + '市')

    elif len(no) == 5:  # gun
        name.append(gun_name_with_suffix(origin_name))

    elif len(no) == 6:  # ku
        if no[0:4] == '1001':    # Tokyo 23 wards
            name.append(origin_name + '区')
        else:
            name = get_no_name_list(no[0:4])
            name.append(origin_name + '区')
    
    return name


def get_no_name(no):
    return ' '.join(get_no_name_list(no))


def is_qsl_received(one_qso):
    if 'QSL_RCVD' in one_qso and one_qso['QSL_RCVD'] == "Y":
        return True
    if 'EQSL_QSL_RCVD' in one_qso and one_qso['EQSL_QSL_RCVD'] == "Y":
        return True
    if 'LOTW_QSL_RCVD' in one_qso and one_qso['LOTW_QSL_RCVD'] == "Y":
        return True
    return False

def is_in_japan(one_qso):
    if 'DXCC' in one_qso and one_qso['DXCC'] in ['339', '177', '192']:
        return True
    return False


def apply_ogasawara_mapping(one_qso):
    if one_qso.get('DXCC') in ['177', '192']:  # Minamitorishima and Ogasawara
        normalized_qso = dict(one_qso)
        normalized_qso['STATE'] = '10'  # Tokyo
        normalized_qso['CNTY'] = '10007'  # Ogasawara
        return normalized_qso
    return one_qso


qsl_list_header = ['No.', 'Callsign', 'Date', 'Band', 'Mode', 'Remarks']
aja_list_header = ['City/Gun/Ku', 'Band', 'Callsign', 'Date', 'Mode', 'Remarks']

def get_info_for_qsl_list(idx, one_qso, remarks):
    if one_qso:
        return [idx, one_qso['CALL'], one_qso['QSO_DATE'], one_qso['BAND'], one_qso['MODE'], remarks]
    else:
        return [idx, '', '', '', '', remarks]

def get_info_for_aja_list(no, one_qso, remarks):
    return [no, one_qso['BAND'], one_qso['CALL'], one_qso['QSO_DATE'], one_qso['MODE'], remarks]


def is_after_date(qso_date, entity_date):
    """Return True if qso_date is strictly after entity_date.
    Both are YYYYMMDD strings; entity_date may be empty."""
    if not entity_date:
        return False
    return qso_date > entity_date


def is_on_or_after_date(qso_date, entity_date):
    """Return True if qso_date is on or after entity_date.
    Both are YYYYMMDD strings; entity_date may be empty."""
    if not entity_date:
        return False
    return qso_date >= entity_date


# ── Band mapping for AJA output ─────────────────────────────────────────────

# ADIF wavelength band -> frequency label (ordered, 15 bands)
BAND_MAP = {
    '160m': '1.9MHz',
    '80m': '3.5MHz',
    '40m': '7MHz',
    '30m': '10MHz',
    '20m': '14MHz',
    '17m': '18MHz',
    '15m': '21MHz',
    '12m': '24MHz',
    '10m': '28MHz',
    '6m': '50MHz',
    '2m': '144MHz',
    '70cm': '430MHz',
    '23cm': '1200MHz',
    '13cm': '2400MHz',
    '6cm': '5600MHz',
}

# Entities to skip when counting AJA (major designated cities)
# AJA_SKIP_LIST = ['1001', '1101', '2001', '2201', '2501', '2701', '4021'] # For Japanese version
AJA_SKIP_LIST = ['1001'] # For English version


def format_date_ymd(date_str):
    """Convert YYYYMMDD to YYYY-MM-DD for display."""
    if not date_str or len(date_str) != 8:
        return date_str
    return date_str[:4] + '-' + date_str[4:6] + '-' + date_str[6:8]


def format_entity_name_for_aja(no):
    """Format entity display name for AJA wide-format output.

    Reuses get_no_name_list() for core name logic, then:
    - Strips the prefecture name (handled separately in column 1).
    - Joins remaining parts with a half-width space.
    - Appends date annotations in unified ' (YYYY-MM-DD)' format.
    """
    if no not in no_list:
        return no

    name_parts = get_no_name_list(no)
    # Remove prefecture name (first element); keep the rest as entity name
    if len(name_parts) > 1:
        entity_parts = name_parts[1:]
    else:
        entity_parts = name_parts

    name = ' '.join(entity_parts)

    # Append annotation for deleted / designated-city dates
    info = no_list[no]
    if info.get('deleted') and info.get('deleted_date'):
        name += '*' + format_date_ymd(info['deleted_date'])
    elif info.get('type') == 'designated city' and info.get('designated_city_date'):
        name += '*' + format_date_ymd(info['designated_city_date'])

    return name


ajd = {}
waja = {}
jcc = {}
jcg = {}
aja = {}

# Load list from CSV file
## AJD
try:
    with open('checksheet_ajd.csv', 'r', newline='', encoding='utf-8-sig') as f:
        csv_reader = csv.reader(f, dialect='excel')
        for row in csv_reader:
            if row[0] == 'No.' or row[1] == '':
                continue
            else:
                this_ajd = row[5].split(' ')[1]
                ajd[this_ajd] = {
                    'CALL': row[1],
                    'QSO_DATE': row[2],
                    'BAND': row[3],
                    'MODE': row[4]
                }
except FileNotFoundError as e:
    print("checksheet_ajd.csv not found. Start new statistics.")

## WAJA
try:
    with open('checksheet_waja.csv', 'r', newline='', encoding='utf-8-sig') as f:
        csv_reader = csv.reader(f, dialect='excel')
        for row in csv_reader:
            if row[0] == 'No.' or row[1] == '':
                continue
            else:
                this_pref = row[5].split(' ')[0]
                waja[this_pref] = {
                    'CALL': row[1],
                    'QSO_DATE': row[2],
                    'BAND': row[3],
                    'MODE': row[4]
                }
except FileNotFoundError as e:
    print("checksheet_waja.csv not found. Start new statistics.")

## JCC
try:
    with open('checksheet_jcc.csv', 'r', newline='', encoding='utf-8-sig') as f:
        csv_reader = csv.reader(f, dialect='excel')
        for row in csv_reader:
            if row[0] == 'No.' or row[1] == '':
                continue
            else:
                this_jcc = row[5].split(' ')[0]
                jcc[this_jcc] = {
                    'CALL': row[1],
                    'QSO_DATE': row[2],
                    'BAND': row[3],
                    'MODE': row[4]
                }
except FileNotFoundError as e:
    print("checksheet_jcc.csv not found. Start new statistics.")

## JCG
try:
    with open('checksheet_jcg.csv', 'r', newline='', encoding='utf-8-sig') as f:
        csv_reader = csv.reader(f, dialect='excel')
        for row in csv_reader:
            if row[0] == 'No.' or row[1] == '':
                continue
            else:
                this_jcg = row[5].split(' ')[0]
                jcg[this_jcg] = {
                    'CALL': row[1],
                    'QSO_DATE': row[2],
                    'BAND': row[3],
                    'MODE': row[4]
                }
except FileNotFoundError as e:
    print("checksheet_jcg.csv not found. Start new statistics.")

## AJA
try:
    with open('checksheet_aja.csv', 'r', newline='', encoding='utf-8-sig') as f:
        csv_reader = csv.reader(f, dialect='excel')
        for row in csv_reader:
            if row[0] == 'City/Gun/Ku' or row[2] == '':
                continue
            else:
                this_no = row[0]
                this_band = row[1]
                aja[(this_no, this_band)] = {
                    'BAND': row[1],
                    'CALL': row[2],
                    'QSO_DATE': row[3],
                    'MODE': row[4]
                }
except FileNotFoundError as e:
    print("checksheet_aja.csv not found. Start new statistics.")

if len(sys.argv) >= 2:
    adif_file = sys.argv[1]
else:
    adif_file = input("Your ADIF File: ").strip('\'\"')

qsos, header = adif_io.read_from_file(adif_file)

for one_qso in qsos:
    this_call = one_qso['CALL']
    this_band = one_qso['BAND']

    if not is_qsl_received(one_qso):
        continue

    if not is_in_japan(one_qso):
        continue

    one_qso = apply_ogasawara_mapping(one_qso)

    if 'STATE' not in one_qso:
        continue
    this_pref = one_qso['STATE']

    if this_call[0] == "J":
        district_call = this_call[2]
    else:
        district_call = '1'
    district_no = get_district(one_qso['STATE'])

    if district_call == district_no:
        if district_call not in ajd or ajd[district_call]['QSO_DATE'] > one_qso['QSO_DATE']:
            ajd[district_call] = one_qso
        if this_pref not in waja or waja[this_pref]['QSO_DATE'] > one_qso['QSO_DATE']:
            waja[this_pref] = one_qso

    if 'CNTY' not in one_qso:
        continue
    this_no = one_qso['CNTY']

    if this_no not in no_list:
        continue

    this_no_info = no_list[this_no]
    this_no_type = this_no_info['type']

    # Skip QSOs for deleted entities when contact is after deletion date
    if this_no_info.get('deleted') and is_after_date(
            one_qso['QSO_DATE'], this_no_info.get('deleted_date', '')):
        print(f"WARNING: QSO with {one_qso['CALL']} on {one_qso['QSO_DATE']}, "
              f"{this_no} {get_no_name(this_no)} "
              f"is deleted on {this_no_info['deleted_date']}, skipped",
              file=sys.stderr)
        continue

    if this_no_type in ('city', 'designated city'):
        if this_no not in jcc or jcc[this_no]['QSO_DATE'] > one_qso['QSO_DATE']:
            jcc[this_no] = one_qso
    elif this_no_type == 'ku':
        if this_no[0:4] not in jcc or jcc[this_no[0:4]]['QSO_DATE'] > one_qso['QSO_DATE']:
            jcc[this_no[0:4]] = one_qso
    elif this_no_type == 'gun':
        if this_no not in jcg or jcg[this_no]['QSO_DATE'] > one_qso['QSO_DATE']:
            jcg[this_no] = one_qso

    # Task 3: designated city — count JCC normally, but skip AJA if QSO is on
    # or after the designation date
    # Task 4: also skip AJA for entities in the hard skip list
    if this_no in AJA_SKIP_LIST:
        pass  # silently skip AJA for these entities
    elif this_no_type == 'designated city' and is_on_or_after_date(
            one_qso['QSO_DATE'], this_no_info.get('designated_city_date', '')):
        print(f"WARNING: QSO with {one_qso['CALL']} on {one_qso['QSO_DATE']}, "
              f"{this_no} {get_no_name(this_no)} "
              f"became designated city on {this_no_info['designated_city_date']}, "
              f"use ku number for AJA",
              file=sys.stderr)
    else:
        if (this_no, this_band) not in aja or \
                aja[(this_no, this_band)]['QSO_DATE'] > one_qso['QSO_DATE']:
            aja[(this_no, this_band)] = one_qso

# Print checksheet
## AJD
with open('checksheet_ajd.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv_writer = csv.writer(f, dialect='excel')
    csv_writer.writerow(qsl_list_header)
    idx = 1
    for d in range(10):
        this_district = "%d" % d
        if this_district in ajd:
            this_row = get_info_for_qsl_list(idx, ajd[this_district], "Area %d" % d)
        else:
            this_row = get_info_for_qsl_list(idx, False, "Area %d" % d)
        csv_writer.writerow(this_row)
        idx += 1

## WAJA
with open('checksheet_waja.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv_writer = csv.writer(f, dialect='excel')
    csv_writer.writerow(qsl_list_header)
    idx = 1
    for d in range(1, 48):
        this_pref = "%02d" % d
        if this_pref in waja:
            this_row = get_info_for_qsl_list(idx, waja[this_pref], "%s %s" % (this_pref, get_pref_name(no=this_pref)))
        else:
            this_row = get_info_for_qsl_list(idx, False, "%s %s" % (this_pref, get_pref_name(this_pref)))
        csv_writer.writerow(this_row)
        idx += 1

## JCC
with open('checksheet_jcc.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv_writer = csv.writer(f, dialect='excel')
    csv_writer.writerow(qsl_list_header)
    idx = 1
    for this_jcc in sorted(jcc):
        mark = ' *' if no_list.get(this_jcc, {}).get('deleted') else ''
        this_row = get_info_for_qsl_list(idx, jcc[this_jcc],
                                         "%s %s%s" % (this_jcc, get_no_name(this_jcc), mark))
        csv_writer.writerow(this_row)
        idx += 1

## JCG
with open('checksheet_jcg.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv_writer = csv.writer(f, dialect='excel')
    csv_writer.writerow(qsl_list_header)
    idx = 1
    for this_jcg in sorted(jcg):
        mark = ' *' if no_list.get(this_jcg, {}).get('deleted') else ''
        this_row = get_info_for_qsl_list(idx, jcg[this_jcg],
                                         "%s %s%s" % (this_jcg, get_no_name(this_jcg), mark))
        csv_writer.writerow(this_row)
        idx += 1

## AJA
with open('checksheet_aja.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv_writer = csv.writer(f, dialect='excel')
    csv_writer.writerow(aja_list_header)
    idx = 1
    for this_aja in sorted(aja):
        mark = ' *' if no_list.get(this_aja[0], {}).get('deleted') else ''
        this_row = get_info_for_aja_list(this_aja[0], aja[this_aja],
                                         "%s%s" % (get_no_name(this_aja[0]), mark))
        csv_writer.writerow(this_row)
        idx += 1

## AJA wide-format export (statistics view only)
with open('aja_list.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv_writer = csv.writer(f, dialect='excel')

    # Row 1: band labels — ,JCC/JCG/Ku,,,1.9MHz,,3.5MHz,...
    header1 = ['', 'JCC/JCG/Ku', '', '']
    for freq in BAND_MAP.values():
        header1.extend([freq, ''])
    csv_writer.writerow(header1)

    # Row 2: sub-headers — ,Name,,Number,Mode,Callsign,Mode,Callsign,...
    header2 = ['', 'Name', '', 'Number']
    for _ in BAND_MAP:
        header2.extend(['Mode', 'Callsign'])
    csv_writer.writerow(header2)

    # Row 3: sub-sub-headers — ,,,,check,Date,check,Date,...
    header3 = ['', '', '', '']
    for _ in BAND_MAP:
        header3.extend(['check', 'Date'])
    csv_writer.writerow(header3)

    # Data rows: iterate all entities in no_list order
    last_pref = None
    for no, info in no_list.items():
        if no == '_meta':
            continue
        no_type = info.get('type', '')
        if no_type not in ('city', 'designated city', 'gun', 'ku'):
            continue
        if no in AJA_SKIP_LIST:
            continue

        this_pref = no[:2]

        # Prefecture name column: only on first entity of each prefecture
        if this_pref != last_pref:
            pref_col = get_pref_name(this_pref) + ' ' + this_pref
            last_pref = this_pref
        else:
            pref_col = ''

        entity_name = format_entity_name_for_aja(no)

        # Build band data: (mode, callsign) for row 1; (check, date) for row 2
        row1_bands = []
        row2_bands = []
        for band in BAND_MAP:
            key = (no, band)
            if key in aja:
                qso = aja[key]
                row1_bands.extend([qso['MODE'], qso['CALL']])
                row2_bands.extend(['', qso['QSO_DATE']])
            else:
                row1_bands.extend(['', ''])
                row2_bands.extend(['', ''])

        # Row 1: entity identity + mode/callsign
        csv_writer.writerow(['', pref_col, entity_name, no] + row1_bands)
        # Row 2: check/date
        csv_writer.writerow(['', '', '', ''] + row2_bands)

## AJA total table (band × entity type statistics, computed from aja dict)
band_jcc = defaultdict(set)
band_jcg = defaultdict(set)
band_ku  = defaultdict(set)

for (no, band), qso in aja.items():
    if band not in BAND_MAP:
        continue
    no_type = no_list.get(no, {}).get('type', '')
    if no_type in ('city', 'designated city'):
        band_jcc[band].add(no)
    elif no_type == 'gun':
        band_jcg[band].add(no)
    elif no_type == 'ku':
        band_ku[band].add(no)

with open('aja_total_table.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv_writer = csv.writer(f, dialect='excel')

    header = ['Band'] + list(BAND_MAP.values()) + ['Total']
    csv_writer.writerow(header)

    jcc_counts = [len(band_jcc.get(band, set())) for band in BAND_MAP]
    csv_writer.writerow(['JCC'] + jcc_counts + [sum(jcc_counts)])

    jcg_counts = [len(band_jcg.get(band, set())) for band in BAND_MAP]
    csv_writer.writerow(['JCG'] + jcg_counts + [sum(jcg_counts)])

    ku_counts = [len(band_ku.get(band, set())) for band in BAND_MAP]
    csv_writer.writerow(['Ku'] + ku_counts + [sum(ku_counts)])

    total_per_band = [jcc_counts[i] + jcg_counts[i] + ku_counts[i] for i in range(len(BAND_MAP))]
    csv_writer.writerow(['Total'] + total_per_band + [sum(total_per_band)])

print("----------JARL AWARDS STATUS----------")
print("AJD:  %d / %d : %d%%" % (len(ajd), 10, len(ajd) * 100 / 10))
print("WAJA: %d / %d : %d%%" % (len(waja), 47, len(waja) * 100 / 47))
print("JCC:  total %d" % len(jcc))
print("JCG:  total %d" % len(jcg))
print("AJA:  total %d" % len(aja))
print("--------------------------------------")

# os.system("pause")
