import { describe, it, expect } from 'vitest'
import { computeAllAwards } from '..'
import type { Qso } from '../../types'
import { NO_LIST, PREF_LIST } from '../jarl'

function qso(overrides: Partial<Qso> = {}): Qso {
  return {
    CALL: 'JE8ABC',
    QSO_DATE: '20220101',
    TIME_ON: '120000',
    BAND: '20m',
    MODE: 'FT8',
    DXCC: '339',
    QSL_RCVD: 'Y',
    ...overrides,
  }
}

describe('JARL shared utilities', () => {
  it('should load entity and prefecture lists', () => {
    expect(Object.keys(NO_LIST).length).toBeGreaterThan(1700)
    expect(Object.keys(PREF_LIST).length).toBe(47)
  })
})

describe('AJD (10 call areas)', () => {
  it('should count QSOs where call area matches prefecture district', () => {
    const qsos: Qso[] = [
      qso({ STATE: '01', CALL: 'JE8ABC' }), // Hokkaido → district 8, JE8 matches
      qso({ STATE: '10', CALL: 'JA1DEF' }), // Tokyo → district 1, JA1 matches
    ]
    const r = computeAllAwards(qsos)
    expect(r.ajdCount).toBe(2)
  })

  it('should reject call area mismatch', () => {
    const qsos: Qso[] = [
      qso({ STATE: '01', CALL: 'JA1DEF' }), // Hokkaido → district 8, JA1 does not match
    ]
    const r = computeAllAwards(qsos)
    expect(r.ajdCount).toBe(0)
  })
})

describe('WAJA (47 prefectures)', () => {
  it('should count QSOs per prefecture where call area matches', () => {
    const qsos: Qso[] = [
      qso({ STATE: '01', CALL: 'JE8ABC' }), // matches
      qso({ STATE: '02', CALL: 'JE7DEF' }), // Aomori → 7, JE7 matches
    ]
    const r = computeAllAwards(qsos)
    expect(r.wajaCount).toBe(2)
    expect(r.waja['01']).toBeTruthy()
    expect(r.waja['02']).toBeTruthy()
  })
})

describe('JCC (cities)', () => {
  it('should count city type entities', () => {
    const qsos: Qso[] = [
      qso({ CNTY: '0104' }), // Hakodate (city)
      qso({ CNTY: '0102' }), // Asahikawa (city)
    ]
    const r = computeAllAwards(qsos)
    expect(r.jcc.count).toBe(2)
  })

  it('should map ku to parent city number', () => {
    const qsos: Qso[] = [
      qso({ CNTY: '010101' }), // Sapporo Chuo-ku → parent 0101
    ]
    const r = computeAllAwards(qsos)
    expect(r.jcc.count).toBe(1)
    expect(r.jcc.data['0101']).toBeTruthy()
  })

  it('should keep the earlier QSO when the date is the same', () => {
    const qsos: Qso[] = [
      qso({ CNTY: '0104', QSO_DATE: '20220101', TIME_ON: '103000', CALL: 'JA1LATE' }),
      qso({ CNTY: '0104', QSO_DATE: '20220101', TIME_ON: '091500', CALL: 'JA1EARLY' }),
    ]

    const r = computeAllAwards(qsos)
    expect(r.jcc.data['0104']?.CALL).toBe('JA1EARLY')
    expect(r.jcc.data['0104']?.TIME_ON).toBe('091500')
  })

  it('should skip QSOs after deletion date', () => {
    const qsos: Qso[] = [
      qso({ CNTY: '0132', QSO_DATE: '20200101' }), // Kameda deleted 19731130, after → skip
    ]
    const r = computeAllAwards(qsos)
    expect(r.jcc.count).toBe(0)
    expect(r.waca.count).toBe(0)
  })

  it('should count QSOs before deletion date', () => {
    const qsos: Qso[] = [
      qso({ CNTY: '0132', QSO_DATE: '19700101' }), // before deleted_date 19731130 → ok
    ]
    const r = computeAllAwards(qsos)
    expect(r.jcc.count).toBe(1)
  })
})

describe('JCG (guns)', () => {
  it('should count gun type entities', () => {
    const qsos: Qso[] = [
      qso({ CNTY: '01015' }), // Esashi-gun
    ]
    const r = computeAllAwards(qsos)
    expect(r.jcg.count).toBe(1)
  })

  it('should not count city as gun', () => {
    const qsos: Qso[] = [
      qso({ CNTY: '0101' }), // Sapporo (designated city)
    ]
    const r = computeAllAwards(qsos)
    expect(r.jcg.count).toBe(0)
  })
})

describe('AJA (per-band entity tracking)', () => {
  it('should count each (entity, band) combination separately', () => {
    const qsos: Qso[] = [
      qso({ CNTY: '0104', BAND: '20m' }), // Hakodate 20m
      qso({ CNTY: '0104', BAND: '40m' }), // Hakodate 40m
      qso({ CNTY: '0102', BAND: '20m' }), // Asahikawa 20m
    ]
    const r = computeAllAwards(qsos)
    expect(r.aja.count).toBe(3)
  })

  it('should skip entities in AJA_SKIP_LIST', () => {
    const qsos: Qso[] = [
      qso({ CNTY: '1001' }), // Tokyo 23 wards → skipped
    ]
    const r = computeAllAwards(qsos)
    expect(r.aja.count).toBe(0)
  })

  it('should skip designated city if QSO after designation date', () => {
    // Sapporo became designated city on 19720401
    const qsos: Qso[] = [
      qso({ CNTY: '0101', QSO_DATE: '20200101' }), // after → skip for AJA
    ]
    const r = computeAllAwards(qsos)
    expect(r.aja.count).toBe(0)
  })

  it('should count designated city if QSO before designation date', () => {
    const qsos: Qso[] = [
      qso({ CNTY: '0101', QSO_DATE: '19700101' }), // before 19720401 → count for AJA
    ]
    const r = computeAllAwards(qsos)
    expect(r.aja.count).toBe(1)
  })

  it('should classify by band type', () => {
    const qsos: Qso[] = [
      qso({ CNTY: '0104', BAND: '20m' }),           // city → JCC
      qso({ CNTY: '01015', BAND: '20m' }),          // gun → JCG
      qso({ CNTY: '010101', BAND: '20m' }),         // ku → Ku
    ]
    const r = computeAllAwards(qsos)
    const jccTotal = Object.values(r.aja.byBandType.jcc).reduce((a, b) => a + b, 0)
    const jcgTotal = Object.values(r.aja.byBandType.jcg).reduce((a, b) => a + b, 0)
    const kuTotal = Object.values(r.aja.byBandType.ku).reduce((a, b) => a + b, 0)
    expect(jccTotal).toBe(1)
    expect(jcgTotal).toBe(1)
    expect(kuTotal).toBe(1)
  })
})

describe('WACA / WAGA (excluding deleted)', () => {
  it('WACA should exclude deleted cities from count, JCC includes them', () => {
    const qsos: Qso[] = [
      qso({ CNTY: '0104', QSO_DATE: '20220101' }),  // active city
      qso({ CNTY: '0132', QSO_DATE: '19700101' }),  // deleted city, QSO before 19731130
    ]
    const r = computeAllAwards(qsos)
    expect(r.jcc.count).toBe(2)   // JCC includes deleted (valid QSO before deletion)
    expect(r.waca.count).toBe(1)  // WACA excludes deleted entities entirely
  })

  it('should skip deleted entity QSOs after deletion date entirely', () => {
    const qsos: Qso[] = [
      qso({ CNTY: '0132', QSO_DATE: '20220101' }),  // after 19731130 → skipped
    ]
    const r = computeAllAwards(qsos)
    expect(r.jcc.count).toBe(0)
    expect(r.waca.count).toBe(0)
  })
})

describe('WAPC (China provinces)', () => {
  it('should count mainland China provinces', () => {
    const qsos: Qso[] = [
      qso({ DXCC: '318', STATE: 'BJ', QSL_RCVD: 'Y' }),
    ]
    const r = computeAllAwards(qsos)
    expect(r.wapc.mixedCount).toBe(1)
    expect(r.wapc.mixed['BJ']).toBeTruthy()
  })

  it('should only count QSL or LoTW confirmed QSOs', () => {
    const qsos: Qso[] = [
      qso({ DXCC: '318', STATE: 'BJ', QSL_RCVD: 'N', LOTW_QSL_RCVD: 'Y', EQSL_QSL_RCVD: 'N' }),
      qso({ DXCC: '318', STATE: 'SH', QSL_RCVD: 'N', LOTW_QSL_RCVD: 'N', EQSL_QSL_RCVD: 'Y' }),
      qso({ DXCC: '318', STATE: 'TJ', QSL_RCVD: 'N', LOTW_QSL_RCVD: 'N', EQSL_QSL_RCVD: 'N' }),
    ]

    const r = computeAllAwards(qsos)
    expect(r.wapc.mixedCount).toBe(1)
    expect(r.wapc.mixed['BJ']).toBeTruthy()
    expect(r.wapc.mixed['SH']).toBeNull()
    expect(r.wapc.mixed['TJ']).toBeNull()
  })

  it('should count TW/HK/MO by DXCC', () => {
    const qsos: Qso[] = [
      qso({ DXCC: '386', STATE: undefined }), // TW
      qso({ DXCC: '321', STATE: undefined }), // HK
      qso({ DXCC: '152', STATE: undefined }), // MO
    ]
    const r = computeAllAwards(qsos)
    expect(r.wapc.mixedCount).toBe(3)
  })

  it('should normalize band values to lowercase for the band matrix', () => {
    const qsos: Qso[] = [
      qso({ DXCC: '318', STATE: 'BJ', BAND: '20M' }),
    ]

    const r = computeAllAwards(qsos)
    expect(r.wapc.band['BJ']['20m']?.CALL).toBe('JE8ABC')
    expect(r.wapc.band['BJ']['20m']?.BAND).toBe('20m')
    expect(r.wapc.bandCounts['20m']).toBe(1)
  })

  it('should derive mode groups from root MODE values and uppercase the stored MODE', () => {
    const qsos: Qso[] = [
      qso({ DXCC: '318', STATE: 'BJ', MODE: 'SSB', APP_LOTW_MODEGROUP: 'DATA' }),
      qso({ DXCC: '318', STATE: 'SH', MODE: 'ft8', APP_LOTW_MODEGROUP: 'PHONE', CALL: 'JA1DATA' }),
      qso({ DXCC: '318', STATE: 'TJ', MODE: 'CW', APP_LOTW_MODEGROUP: 'DATA', CALL: 'JA1CW' }),
    ]

    const r = computeAllAwards(qsos)
    expect(r.wapc.mode['BJ']['PHONE']?.CALL).toBe('JE8ABC')
    expect(r.wapc.mode['BJ']['PHONE']?.MODE).toBe('SSB')
    expect(r.wapc.mode['SH']['DATA']?.CALL).toBe('JA1DATA')
    expect(r.wapc.mode['SH']['DATA']?.MODE).toBe('FT8')
    expect(r.wapc.mode['TJ']['CW']?.CALL).toBe('JA1CW')
    expect(r.wapc.modeCounts['DATA']).toBe(1)
    expect(r.wapc.modeCounts['PHONE']).toBe(1)
    expect(r.wapc.modeCounts['CW']).toBe(1)
  })

  it('should treat import-only and unknown MODE values as DATA', () => {
    const qsos: Qso[] = [
      qso({ DXCC: '318', STATE: 'GD', MODE: 'USB' }),
      qso({ DXCC: '318', STATE: 'GX', MODE: 'PSK31', CALL: 'JA1PSK31' }),
      qso({ DXCC: '318', STATE: 'CQ', MODE: 'NOT_A_REAL_MODE', CALL: 'JA1UNKNOWN' }),
    ]

    const r = computeAllAwards(qsos)
    expect(r.wapc.mixed['GD']?.CALL).toBe('JE8ABC')
    expect(r.wapc.mixed['GX']?.CALL).toBe('JA1PSK31')
    expect(r.wapc.mode['GD']['DATA']?.CALL).toBe('JE8ABC')
    expect(r.wapc.mode['GX']['DATA']?.CALL).toBe('JA1PSK31')
    expect(r.wapc.mode['CQ']['DATA']?.CALL).toBe('JA1UNKNOWN')
    expect(r.wapc.modeCounts['CW']).toBe(0)
    expect(r.wapc.modeCounts['PHONE']).toBe(0)
    expect(r.wapc.modeCounts['DATA']).toBe(3)
  })
})

describe('Computed result completeness', () => {
  it('should compute all awards from an empty QSO list', () => {
    const r = computeAllAwards([])
    expect(r.ajdCount).toBe(0)
    expect(r.wajaCount).toBe(0)
    expect(r.jcc.count).toBe(0)
    expect(r.jcg.count).toBe(0)
    expect(r.aja.count).toBe(0)
    expect(r.waca.count).toBe(0)
    expect(r.waga.count).toBe(0)
    expect(r.wapc.mixedCount).toBe(0)
    expect(r.wcsa.schoolCount).toBe(0)
    expect(r.wcsa.slotCount).toBe(0)
  })
})

describe('WCSA (Chinese schools)', () => {
  it('should count paper QSL and LoTW but not eQSL', () => {
    const qsos: Qso[] = [
      qso({ CALL: 'BY1QH', BAND: '20m', QSL_RCVD: 'Y' }),
      qso({ CALL: 'BY1HT', BAND: '40m', QSL_RCVD: 'N', LOTW_QSL_RCVD: 'Y' }),
      qso({ CALL: 'BY6DX', BAND: '15m', QSL_RCVD: 'N', LOTW_QSL_RCVD: 'N', EQSL_QSL_RCVD: 'Y' }),
    ]

    const r = computeAllAwards(qsos)
    expect(r.wcsa.schoolCount).toBe(2)
    expect(r.wcsa.slotCount).toBe(2)
  })

  it('should deduplicate normal slots by raw call, band, and mode', () => {
    const qsos: Qso[] = [
      qso({ CALL: 'BY1QH', BAND: '20m', MODE: 'FT8', QSO_DATE: '20260102' }),
      qso({ CALL: 'BY1QH', BAND: '20M', MODE: 'ft8', QSO_DATE: '20260101' }),
      qso({ CALL: 'BY1QH', BAND: '40m', MODE: 'FT8', QSO_DATE: '20260103' }),
    ]

    const r = computeAllAwards(qsos)
    expect(r.wcsa.schoolCount).toBe(1)
    expect(r.wcsa.slotCount).toBe(2)
    expect(r.wcsa.slots.get('BY1QH|20M|FT8')?.qso.QSO_DATE).toBe('20260101')
  })

  it('should use satellite and mode for SAT slots', () => {
    const qsos: Qso[] = [
      qso({ CALL: 'BY1QH', PROP_MODE: 'SAT', SAT_NAME: 'IO-117', BAND: '70cm', MODE: 'FT4', QSO_DATE: '20260102' }),
      qso({ CALL: 'BY1QH', PROP_MODE: 'SAT', SAT_NAME: 'io-117', BAND: '2m', MODE: 'FT4', QSO_DATE: '20260101' }),
      qso({ CALL: 'BY1QH', PROP_MODE: 'SAT', SAT_NAME: 'FO-29', BAND: '2m', MODE: 'FT4', QSO_DATE: '20260103' }),
    ]

    const r = computeAllAwards(qsos)
    expect(r.wcsa.slotCount).toBe(2)
    expect(r.wcsa.slots.get('BY1QH|SAT|IO-117|FT4')?.qso.QSO_DATE).toBe('20260101')
  })

  it('should include EME and MS propagation mode in slot keys', () => {
    const qsos: Qso[] = [
      qso({ CALL: 'BY1QH', PROP_MODE: 'EME', BAND: '2m', MODE: 'CW' }),
      qso({ CALL: 'BY1QH', PROP_MODE: 'MS', BAND: '2m', MODE: 'CW', QSO_DATE: '20260102' }),
      qso({ CALL: 'BY1QH', BAND: '2m', MODE: 'CW', QSO_DATE: '20260103' }),
    ]

    const r = computeAllAwards(qsos)
    expect(r.wcsa.slotCount).toBe(3)
    expect(r.wcsa.slots.has('BY1QH|2M|CW|EME')).toBe(true)
    expect(r.wcsa.slots.has('BY1QH|2M|CW|MS')).toBe(true)
    expect(r.wcsa.slots.has('BY1QH|2M|CW')).toBe(true)
  })

  it('should use raw call for slots and school call for school counts', () => {
    const qsos: Qso[] = [
      qso({ CALL: 'BY1QH', BAND: '20m', MODE: 'FT8' }),
      qso({ CALL: 'BY1QH/P', BAND: '20m', MODE: 'FT8' }),
      qso({ CALL: 'BA7/BY1QH', BAND: '20m', MODE: 'FT8' }),
    ]

    const r = computeAllAwards(qsos)
    expect(r.wcsa.schoolCount).toBe(1)
    expect(r.wcsa.slotCount).toBe(3)
    expect(r.wcsa.slotCountsBySchool.BY1QH).toBe(3)
    expect(r.wcsa.slots.has('BY1QH|20M|FT8')).toBe(true)
    expect(r.wcsa.slots.has('BY1QH/P|20M|FT8')).toBe(true)
    expect(r.wcsa.slots.has('BA7/BY1QH|20M|FT8')).toBe(true)
  })

  it('should evaluate Bronze, Silver, and Gold thresholds', () => {
    const qsos: Qso[] = [
      qso({ CALL: 'BY1QH', BAND: '20m', MODE: 'FT8' }),
      qso({ CALL: 'BY1QH', BAND: '40m', MODE: 'FT8' }),
      qso({ CALL: 'BY1QH', BAND: '15m', MODE: 'FT8' }),
      qso({ CALL: 'BY1HT', BAND: '20m', MODE: 'FT8' }),
      qso({ CALL: 'BY1HT', BAND: '40m', MODE: 'FT8' }),
      qso({ CALL: 'BY1HT', BAND: '15m', MODE: 'FT8' }),
      qso({ CALL: 'BY6DX', BAND: '20m', MODE: 'FT8' }),
      qso({ CALL: 'BY6DX', BAND: '40m', MODE: 'FT8' }),
      qso({ CALL: 'BY6DX', BAND: '15m', MODE: 'FT8' }),
      qso({ CALL: 'BY6DX', BAND: '10m', MODE: 'FT8' }),
    ]

    const r = computeAllAwards(qsos)
    const levels = Object.fromEntries(r.wcsa.levels.map((level) => [level.name, level]))
    expect(levels.Bronze.achieved).toBe(true)
    expect(levels.Silver.achieved).toBe(true)
    expect(levels.Gold.achieved).toBe(true)
  })

  it('should skip unknown, unconfirmed, and incomplete QSOs', () => {
    const qsos: Qso[] = [
      qso({ CALL: 'BY9NOPE' }),
      qso({ CALL: 'BY1QH', QSL_RCVD: 'N', LOTW_QSL_RCVD: 'N' }),
      qso({ CALL: 'BY1HT', BAND: '', MODE: 'FT8' }),
      qso({ CALL: 'BY6DX', PROP_MODE: 'SAT', SAT_NAME: '', MODE: 'FT8' }),
    ]

    const r = computeAllAwards(qsos)
    expect(r.wcsa.schoolCount).toBe(0)
    expect(r.wcsa.slotCount).toBe(0)
  })
})
