def is_qsl_received(qso):
    """Return True when a QSO is confirmed by paper QSL or LoTW."""
    if qso.get('QSL_RCVD', '').upper() == 'Y':
        return True
    if qso.get('LOTW_QSL_RCVD', '').upper() == 'Y':
        return True
    return False

