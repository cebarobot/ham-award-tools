import { describe, expect, it } from 'vitest'
import { parseAdifText } from '../useAdifParser'

describe('ADIF parser', () => {
  it('should preserve satellite propagation fields', () => {
    const qsos = parseAdifText('<EOH><CALL:5>BY1QH<PROP_MODE:3>SAT<SAT_NAME:6>IO-117<QSO_DATE:8>20260101<BAND:3>70cm<MODE:3>FT4<QSL_RCVD:1>Y<EOR>')

    expect(qsos).toHaveLength(1)
    expect(qsos[0].PROP_MODE).toBe('SAT')
    expect(qsos[0].SAT_NAME).toBe('IO-117')
  })
})

