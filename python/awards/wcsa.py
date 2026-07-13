import json
import sys

from common.qsl import is_qsl_received


AWARD_LEVELS = [
    ('Bronze', 1, 3),
    ('Silver', 2, 6),
    ('Gold', 3, 10),
]


def load_school_list(path_to_school_list):
    with open(path_to_school_list, 'r', encoding='utf-8') as f:
        schools = json.load(f)

    return schools


def compute_wcsa(qsos, schools, warning_stream=sys.stderr):
    normalized_schools = {call.upper(): name for call, name in schools.items()}
    slots = {}

    for qso in qsos:
        normalized_qso = _normalize_qso(qso)
        school_call = _get_school_call(normalized_qso.get('CALL', ''), normalized_schools)

        if not school_call:
            continue
        if not is_qsl_received(normalized_qso):
            continue

        slot_key = _get_slot_key(normalized_qso, warning_stream)
        if slot_key is None:
            continue

        existing = slots.get(slot_key)
        if existing is None or _qso_stamp(normalized_qso) < _qso_stamp(existing['QSO']):
            slots[slot_key] = {
                'SCHOOL_CALL': school_call,
                'SCHOOL_NAME': normalized_schools[school_call],
                'QSO': normalized_qso,
            }

    return _build_result(slots)


def _normalize_qso(qso):
    normalized_qso = {}
    for key, value in qso.items():
        normalized_qso[str(key).upper()] = '' if value is None else str(value).strip()

    for key in ('CALL', 'MODE', 'PROP_MODE', 'SAT_NAME'):
        if key in normalized_qso:
            normalized_qso[key] = normalized_qso[key].upper()

    return normalized_qso


def _get_school_call(call, schools):
    normalized_call = call.strip().upper()
    if normalized_call in schools:
        return normalized_call

    for part in normalized_call.split('/'):
        if part in schools:
            return part

    return None


def _get_slot_key(qso, warning_stream):
    call = qso.get('CALL', '').upper()
    prop_mode = qso.get('PROP_MODE', '').upper()

    required_fields = ['CALL', 'QSO_DATE', 'MODE']
    if prop_mode == 'SAT':
        required_fields.append('SAT_NAME')
    else:
        required_fields.append('BAND')

    missing_fields = [field for field in required_fields if not qso.get(field)]
    if missing_fields:
        print(
            "WARNING: QSO with %s is missing required field(s): %s, skipped" % (
                call or 'UNKNOWN',
                ', '.join(missing_fields),
            ),
            file=warning_stream,
        )
        return None

    mode = qso['MODE'].upper()
    if prop_mode == 'SAT':
        return (call, 'SAT', qso['SAT_NAME'].upper(), mode)
    if prop_mode in ('EME', 'MS'):
        return (call, qso['BAND'].upper(), mode, prop_mode)
    return (call, qso['BAND'].upper(), mode)


def _build_result(slots):
    school_calls = sorted({slot['SCHOOL_CALL'] for slot in slots.values()})
    slot_counts_by_school = {}
    for school_call in school_calls:
        slot_counts_by_school[school_call] = 0
    for slot in slots.values():
        slot_counts_by_school[slot['SCHOOL_CALL']] += 1

    school_count = len(school_calls)
    slot_count = len(slots)
    levels = []
    for name, required_schools, required_slots in AWARD_LEVELS:
        levels.append({
            'NAME': name,
            'REQUIRED_SCHOOLS': required_schools,
            'REQUIRED_SLOTS': required_slots,
            'ACHIEVED': school_count >= required_schools and slot_count >= required_slots,
        })

    return {
        'SLOTS': slots,
        'SCHOOL_COUNT': school_count,
        'SLOT_COUNT': slot_count,
        'LEVELS': levels,
        'SLOT_COUNTS_BY_SCHOOL': slot_counts_by_school,
    }


def _qso_stamp(qso):
    return qso.get('QSO_DATE', '') + qso.get('TIME_ON', '')
