import io
import sys
import unittest
from pathlib import Path


PYTHON_DIR = Path(__file__).resolve().parents[1]
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from awards.wcsa import compute_wcsa  # noqa: E402


SCHOOLS = {
    'BY1QH': 'Tsinghua University',
    'BY1HT': 'Beihang University',
    'BY6DX': 'University of Science and Technology of China',
}


def qso(**overrides):
    data = {
        'CALL': 'BY1QH',
        'QSO_DATE': '20260101',
        'TIME_ON': '120000',
        'BAND': '20m',
        'MODE': 'FT8',
        'QSL_RCVD': 'Y',
    }
    data.update(overrides)
    return data


class WcsaTest(unittest.TestCase):
    def test_counts_paper_qsl_and_lotw_but_not_eqsl(self):
        result = compute_wcsa([
            qso(CALL='BY1QH', BAND='20m', QSL_RCVD='Y'),
            qso(CALL='BY1HT', BAND='40m', QSL_RCVD='N', LOTW_QSL_RCVD='Y'),
            qso(CALL='BY6DX', BAND='15m', QSL_RCVD='N', LOTW_QSL_RCVD='N', EQSL_QSL_RCVD='Y'),
        ], SCHOOLS)

        self.assertEqual(result['SCHOOL_COUNT'], 2)
        self.assertEqual(result['SLOT_COUNT'], 2)

    def test_deduplicates_normal_slot_by_call_band_mode(self):
        result = compute_wcsa([
            qso(CALL='BY1QH', BAND='20m', MODE='FT8', QSO_DATE='20260102'),
            qso(CALL='BY1QH', BAND='20M', MODE='ft8', QSO_DATE='20260101'),
            qso(CALL='BY1QH', BAND='40m', MODE='FT8', QSO_DATE='20260103'),
        ], SCHOOLS)

        self.assertEqual(result['SCHOOL_COUNT'], 1)
        self.assertEqual(result['SLOT_COUNT'], 2)
        retained = result['SLOTS'][('BY1QH', '20M', 'FT8')]
        self.assertEqual(retained['QSO']['QSO_DATE'], '20260101')

    def test_sat_slot_uses_satellite_and_mode_not_band(self):
        result = compute_wcsa([
            qso(PROP_MODE='SAT', SAT_NAME='IO-117', BAND='70cm', MODE='FT4', QSO_DATE='20260102'),
            qso(PROP_MODE='SAT', SAT_NAME='io-117', BAND='2m', MODE='FT4', QSO_DATE='20260101'),
            qso(PROP_MODE='SAT', SAT_NAME='FO-29', BAND='2m', MODE='FT4', QSO_DATE='20260103'),
        ], SCHOOLS)

        self.assertEqual(result['SLOT_COUNT'], 2)
        retained = result['SLOTS'][('BY1QH', 'SAT', 'IO-117', 'FT4')]
        self.assertEqual(retained['QSO']['QSO_DATE'], '20260101')

    def test_eme_and_ms_include_prop_mode_in_slot_key(self):
        result = compute_wcsa([
            qso(PROP_MODE='EME', BAND='2m', MODE='CW'),
            qso(PROP_MODE='MS', BAND='2m', MODE='CW', QSO_DATE='20260102'),
            qso(BAND='2m', MODE='CW', QSO_DATE='20260103'),
        ], SCHOOLS)

        self.assertEqual(result['SLOT_COUNT'], 3)
        self.assertIn(('BY1QH', '2M', 'CW', 'EME'), result['SLOTS'])
        self.assertIn(('BY1QH', '2M', 'CW', 'MS'), result['SLOTS'])
        self.assertIn(('BY1QH', '2M', 'CW'), result['SLOTS'])

    def test_keeps_earliest_qso_for_same_slot(self):
        result = compute_wcsa([
            qso(QSO_DATE='20260101', TIME_ON='120000', MODE='SSB'),
            qso(QSO_DATE='20260101', TIME_ON='080000', MODE='SSB'),
            qso(QSO_DATE='20251231', TIME_ON='230000', MODE='SSB'),
        ], SCHOOLS)

        retained = result['SLOTS'][('BY1QH', '20M', 'SSB')]
        self.assertEqual(retained['QSO']['QSO_DATE'], '20251231')
        self.assertEqual(retained['QSO']['TIME_ON'], '230000')

    def test_matches_school_calls_with_slash_prefix_or_suffix(self):
        result = compute_wcsa([
            qso(CALL='BY1QH/P', BAND='20m'),
            qso(CALL='BA7/BY1HT', BAND='40m'),
            qso(CALL='BY6DX/7', BAND='15m'),
        ], SCHOOLS)

        self.assertEqual(result['SCHOOL_COUNT'], 3)
        self.assertEqual(result['SLOT_COUNT'], 3)
        self.assertIn(('BY1QH/P', '20M', 'FT8'), result['SLOTS'])
        self.assertIn(('BA7/BY1HT', '40M', 'FT8'), result['SLOTS'])
        self.assertIn(('BY6DX/7', '15M', 'FT8'), result['SLOTS'])
        self.assertEqual(result['SLOTS'][('BY1QH/P', '20M', 'FT8')]['SCHOOL_CALL'], 'BY1QH')

    def test_slots_use_raw_call_but_schools_use_school_call(self):
        result = compute_wcsa([
            qso(CALL='BY1QH', BAND='20m', MODE='FT8'),
            qso(CALL='BY1QH/P', BAND='20m', MODE='FT8'),
            qso(CALL='BA7/BY1QH', BAND='20m', MODE='FT8'),
        ], SCHOOLS)

        self.assertEqual(result['SCHOOL_COUNT'], 1)
        self.assertEqual(result['SLOT_COUNT'], 3)
        self.assertEqual(result['SLOT_COUNTS_BY_SCHOOL']['BY1QH'], 3)
        self.assertIn(('BY1QH', '20M', 'FT8'), result['SLOTS'])
        self.assertIn(('BY1QH/P', '20M', 'FT8'), result['SLOTS'])
        self.assertIn(('BA7/BY1QH', '20M', 'FT8'), result['SLOTS'])

    def test_award_level_thresholds(self):
        result = compute_wcsa([
            qso(CALL='BY1QH', BAND='20m', MODE='FT8'),
            qso(CALL='BY1QH', BAND='40m', MODE='FT8'),
            qso(CALL='BY1QH', BAND='15m', MODE='FT8'),
            qso(CALL='BY1HT', BAND='20m', MODE='FT8'),
            qso(CALL='BY1HT', BAND='40m', MODE='FT8'),
            qso(CALL='BY1HT', BAND='15m', MODE='FT8'),
            qso(CALL='BY6DX', BAND='20m', MODE='FT8'),
            qso(CALL='BY6DX', BAND='40m', MODE='FT8'),
            qso(CALL='BY6DX', BAND='15m', MODE='FT8'),
            qso(CALL='BY6DX', BAND='10m', MODE='FT8'),
        ], SCHOOLS)

        levels = {level['NAME']: level for level in result['LEVELS']}
        self.assertTrue(levels['Bronze']['ACHIEVED'])
        self.assertTrue(levels['Silver']['ACHIEVED'])
        self.assertTrue(levels['Gold']['ACHIEVED'])
        self.assertEqual(result['SCHOOL_COUNT'], 3)
        self.assertEqual(result['SLOT_COUNT'], 10)

    def test_skips_unknown_unconfirmed_and_missing_required_fields(self):
        warnings = io.StringIO()
        result = compute_wcsa([
            qso(CALL='BY9NOPE'),
            qso(CALL='BY1QH', QSL_RCVD='N', LOTW_QSL_RCVD='N'),
            qso(CALL='BY1HT', BAND='', MODE='FT8'),
            qso(CALL='BY6DX', PROP_MODE='SAT', SAT_NAME='', MODE='FT8'),
        ], SCHOOLS, warning_stream=warnings)

        self.assertEqual(result['SCHOOL_COUNT'], 0)
        self.assertEqual(result['SLOT_COUNT'], 0)
        self.assertIn('BAND', warnings.getvalue())
        self.assertIn('SAT_NAME', warnings.getvalue())


if __name__ == '__main__':
    unittest.main()
