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

def get_info_for_qsl_list(idx, one_qso, remarks):
    if one_qso:
        return [idx, one_qso['CALL'], one_qso['QSO_DATE'], one_qso['BAND'], one_qso['MODE'], remarks]
    else:
        return [idx, '', '', '', '', remarks]

ajd = {}
waja = {}
jcc = {}
jcg = {}
aja = {}

if len(sys.argv) >= 2:
    adif_file = sys.argv[1]
else:
    adif_file = input("Your ADIF File: ")

qsos, header = adif_io.read_from_file(adif_file)

for one_qso in qsos:
    if one_qso['COUNTRY'] != "JAPAN":
        continue
    if not 'STATE' in one_qso:
        continue
    if not 'CNTY' in one_qso:
        continue

    this_call = one_qso['CALL']
    this_band = one_qso['BAND']
    this_pref = one_qso['STATE']
    this_no = one_qso['CNTY']

    if this_call[0] == "J":
        district_call = this_call[2]
    else:
        adistrict_call = '1'
    district_no = get_district(one_qso['STATE'])

    if district_call == district_no:
        if not district_call in ajd:
            ajd[district_call] = one_qso
        if not this_pref in waja:
            waja[this_pref] = one_qso

    this_no_info = no_list[this_no]
    this_no_type = this_no_info['type']

    if this_no_type == 'City':
        if not this_no in jcc:
            jcc[this_no] = one_qso
    elif this_no_type == 'Ku':
        if not this_no[0:4] in jcc:
            jcc[this_no[0:4]] = one_qso
    elif this_no_type == 'Gun':
        if not this_no in jcg:
            jcg[this_no] = one_qso

    if not (this_band, this_no) in aja:
        aja[(this_band, this_no)] = one_qso

jcc = {k: jcc[k] for k in sorted(jcc)}
jcg = {k: jcg[k] for k in sorted(jcg)}

# AJD
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

# WAJA
with open('checksheet_waja.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv_writer = csv.writer(f, dialect='excel')
    csv_writer.writerow(qsl_list_header)
    idx = 1
    for d in range(1, 48):
        this_pref = "%02d" % d
        if this_pref in waja:
            this_row = get_info_for_qsl_list(idx, waja[this_pref], "%s (%s)" % (get_no_name(this_pref), this_pref))
        else:
            this_row = get_info_for_qsl_list(idx, False, "%s (%s)" % (get_no_name(this_pref), this_pref))
        csv_writer.writerow(this_row)
        idx += 1

# JCC
with open('checksheet_jcc.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv_writer = csv.writer(f, dialect='excel')
    csv_writer.writerow(qsl_list_header)
    idx = 1
    for this_jcc in jcc:
        this_row = get_info_for_qsl_list(idx, jcc[this_jcc], "%s (%s)" % (get_no_name(this_jcc), this_jcc))
        csv_writer.writerow(this_row)
        idx += 1

# JCG
with open('checksheet_jcg.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv_writer = csv.writer(f, dialect='excel')
    csv_writer.writerow(qsl_list_header)
    idx = 1
    for this_jcg in jcg:
        this_row = get_info_for_qsl_list(idx, jcg[this_jcg], "%s (%s)" % (get_no_name(this_jcg), this_jcg))
        csv_writer.writerow(this_row)
        idx += 1

print("----------JARL AWARDS STATUS----------")
print("JCC:  total %d" % len(jcc))
print("JCG:  total %d" % len(jcg))
print("AJD:  %d / %d : %d%%" % (len(ajd), 10, len(ajd) * 100 / 10))
print("WAJA: %d / %d : %d%%" % (len(waja), 47, len(waja) * 100 / 47))
print("AJA:  total %d" % len(aja))
print("--------------------------------------")

# os.system("pause")
