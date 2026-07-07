import os
import sys
import adif_io
import csv

dxcc_china = '318'
dxcc_other = {
    '386': 'TW',
    '321': 'HK',
    '152': 'MO'
}

province_list = [
    'BJ', 'HL', 'JL', 'LN', 'TJ', 'NM', 'HE', 'SX', 'SH', 'SD', 
    'JS', 'ZJ', 'JX', 'FJ', 'AH', 'HA', 'HB', 'HN', 'GD', 'GX', 
    'HI', 'SC', 'CQ', 'GZ', 'YN', 'SN', 'GS', 'NX', 'QH', 'XJ', 
    'XZ', 'TW', 'HK', 'MO'
]

band_list = [
    '160m', '80m', '40m', '30m', '20m', '17m', '15m', '12m', '10m'
]

mode_group_list = [
    'CW', 'PHONE', 'DATA'
]

root_mode_groups = {
    'AM': 'PHONE',
    'CW': 'CW',
    'DIGITALVOICE': 'PHONE',
    'FM': 'PHONE',
    'SSB': 'PHONE',
    'VOI': 'PHONE',
}

def init_slot(list=[]):
    slot = dict()
    for province in province_list:
        if list:
            slot[province] = dict()
            for x in list:
                slot[province][x] = None
        else:
            slot[province] = None
    return slot

def init_cnt(list):
    cnt = dict()
    for x in list:
        cnt[x] = 0
    return cnt


if len(sys.argv) >= 2:
    adif_file = sys.argv[1]
else:
    adif_file = input("Your ADIF File: ").strip('\'\"')

qsos, header = adif_io.read_from_file(adif_file)

slot_mix = init_slot()
slot_band = init_slot(band_list)
slot_mode = init_slot(mode_group_list)

cnt_mix = 0
cnt_band = init_cnt(band_list)
cnt_mode = init_cnt(mode_group_list)

for one_qso in qsos:
    # print(one_qso)

    this_province = None

    if 'DXCC' not in one_qso:
        continue

    if one_qso['DXCC'] == dxcc_china and 'STATE' in one_qso:
        this_province = one_qso['STATE'].upper()
    elif one_qso['DXCC'] in dxcc_other:
        this_province = dxcc_other[one_qso['DXCC']]

    if not this_province or this_province not in province_list:
        continue

    qso_info = {
        'CALL': one_qso['CALL'],
        'QSO_DATE': one_qso['QSO_DATE'],
        'TIME_ON': one_qso.get('TIME_ON', ''),
        'BAND': one_qso['BAND'].lower(),
        'MODE': one_qso['MODE'].upper(),
        'MODE_GROUP': root_mode_groups.get(one_qso['MODE'].upper(), 'DATA')
    }

    if not slot_mix[this_province]:
        slot_mix[this_province] = qso_info
    if qso_info['BAND'] in band_list and not slot_band[this_province][qso_info['BAND']]:
        slot_band[this_province][qso_info['BAND']] = qso_info
    if not slot_mode[this_province][qso_info['MODE_GROUP']]:
        slot_mode[this_province][qso_info['MODE_GROUP']] = qso_info

print("WAPC Award Statistics")

with open('wapc_checksheet_band.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv_writer = csv.writer(f, dialect='excel')
    csv_writer.writerow(['Province', 'MIXED'] + band_list)
    for this_province in province_list:
        row = [this_province]
        
        if slot_mix[this_province]:
            row.append(slot_mix[this_province]['CALL'])
            cnt_mix += 1
        else:
            row.append('')
        
        for this_band in band_list:
            if slot_band[this_province][this_band]:
                row.append(slot_band[this_province][this_band]['CALL'])
                cnt_band[this_band] += 1
            else:
                row.append('')

        csv_writer.writerow(row)

print("MIXED\t%d\t%d%%" % (cnt_mix, cnt_mix * 100 / len(province_list)))

for x in band_list:
    print("%s\t%d\t%d%%" % (x, cnt_band[x], cnt_band[x] * 100 / len(province_list)))


with open('wapc_checksheet_mode.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv_writer = csv.writer(f, dialect='excel')
    csv_writer.writerow(['Province'] + mode_group_list)
    for this_province in province_list:
        row = [this_province]
        
        for this_mode in mode_group_list:
            if slot_mode[this_province][this_mode]:
                row.append(slot_mode[this_province][this_mode]['CALL'])
                cnt_mode[this_mode] += 1
            else:
                row.append('')

        csv_writer.writerow(row)

for x in mode_group_list:
    print("%s\t%d\t%d%%" % (x, cnt_mode[x], cnt_mode[x] * 100 / len(province_list)))

# os.system("pause")
