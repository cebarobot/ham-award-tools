import sys
import os
from os import path
import adif_io
import csv
import json

NO_NAME_TYPE = 'kanji'

path_to_no_list = path.abspath(path.join(path.dirname(__file__), 'no-list.json'))

with open(path_to_no_list, "r", encoding="utf-8") as f:
    no_list = json.load(f)

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

def get_no_name(no):
    if no not in no_list:
        return 'ERROR'
    no_info = no_list[no]
    if no_info['type'] == 'Prefecture':
        return no_info[NO_NAME_TYPE]
    elif no_info['type'] == 'City' or no_info['type'] == 'Gun':
        return get_no_name(no[0:2]) + ' ' + no_info[NO_NAME_TYPE]
    elif no_info['type'] == 'Ku':
        return get_no_name(no[0:4]) + ' ' + no_info[NO_NAME_TYPE]
    return 'ERROR'



qsl_list_header = ['No.', 'Callsign', 'Date', 'Band', 'Mode', 'Remarks']
aja_list_header = ['City/Gun/Ku', 'Band', 'Callsign', 'Date', 'Mode', 'Remarks']

def get_info_for_qsl_list(idx, one_qso, remarks):
    if one_qso:
        return [idx, one_qso['CALL'], one_qso['QSO_DATE'], one_qso['BAND'], one_qso['MODE'], remarks]
    else:
        return [idx, '', '', '', '', remarks]

def get_info_for_aja_list(no, one_qso, remarks):
    return [no, one_qso['BAND'], one_qso['CALL'], one_qso['QSO_DATE'], one_qso['MODE'], remarks]

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

    if 'QSL_RCVD' not in one_qso or one_qso['QSL_RCVD'] != "Y":
        continue

    if 'COUNTRY' not in one_qso or one_qso['COUNTRY'] != "JAPAN":
        continue

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

    # TODO: check delete JCC/JCG/Ku with delete Date

    this_no_info = no_list[this_no]
    this_no_type = this_no_info['type']

    if this_no_type == 'City':
        if this_no not in jcc or jcc[this_no]['QSO_DATE'] > one_qso['QSO_DATE']:
            jcc[this_no] = one_qso
    elif this_no_type == 'Ku':
        if this_no[0:4] not in jcc or jcc[this_no[0:4]]['QSO_DATE'] > one_qso['QSO_DATE']:
            jcc[this_no[0:4]] = one_qso
    elif this_no_type == 'Gun':
        if this_no not in jcg or jcg[this_no]['QSO_DATE'] > one_qso['QSO_DATE']:
            jcg[this_no] = one_qso

    if (this_no, this_band) not in aja or aja[(this_no, this_band)]['QSO_DATE'] > one_qso['QSO_DATE']:
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
            this_row = get_info_for_qsl_list(idx, waja[this_pref], "%s %s" % (this_pref, get_no_name(this_pref)))
        else:
            this_row = get_info_for_qsl_list(idx, False, "%s %s" % (this_pref, get_no_name(this_pref)))
        csv_writer.writerow(this_row)
        idx += 1

## JCC
with open('checksheet_jcc.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv_writer = csv.writer(f, dialect='excel')
    csv_writer.writerow(qsl_list_header)
    idx = 1
    for this_jcc in sorted(jcc):
        this_row = get_info_for_qsl_list(idx, jcc[this_jcc], "%s %s" % (this_jcc, get_no_name(this_jcc)))
        csv_writer.writerow(this_row)
        idx += 1

## JCG
with open('checksheet_jcg.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv_writer = csv.writer(f, dialect='excel')
    csv_writer.writerow(qsl_list_header)
    idx = 1
    for this_jcg in sorted(jcg):
        this_row = get_info_for_qsl_list(idx, jcg[this_jcg], "%s %s" % (this_jcg, get_no_name(this_jcg)))
        csv_writer.writerow(this_row)
        idx += 1

## AJA
with open('checksheet_aja.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv_writer = csv.writer(f, dialect='excel')
    csv_writer.writerow(aja_list_header)
    idx = 1
    for this_aja in sorted(aja):
        this_row = get_info_for_aja_list(this_aja[0], aja[this_aja], "%s" % (get_no_name(this_aja[0])))
        csv_writer.writerow(this_row)
        idx += 1

print("----------JARL AWARDS STATUS----------")
print("AJD:  %d / %d : %d%%" % (len(ajd), 10, len(ajd) * 100 / 10))
print("WAJA: %d / %d : %d%%" % (len(waja), 47, len(waja) * 100 / 47))
print("JCC:  total %d" % len(jcc))
print("JCG:  total %d" % len(jcg))
print("AJA:  total %d" % len(aja))
print("--------------------------------------")

# os.system("pause")
