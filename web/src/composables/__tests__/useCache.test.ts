import { describe, expect, it } from 'vitest'
import { reactive } from 'vue'
import type { Qso } from '../../types'
import { normalizeQso } from '../useCache'

function makeQso(): Qso {
  return {
    CALL: 'JA1ABC',
    QSO_DATE: '20240101',
    TIME_ON: '120000',
    BAND: '20m',
    MODE: 'CW',
    DXCC: '339',
  }
}

describe('useCache normalization', () => {
  it('turns a reactive QSO proxy into a structured-cloneable plain object', () => {
    const proxiedQso = reactive(makeQso())

    try {
      structuredClone(proxiedQso)
      throw new Error('Expected structuredClone to fail for a reactive proxy')
    } catch (error) {
      expect(error).toBeInstanceOf(DOMException)
      expect((error as DOMException).name).toBe('DataCloneError')
    }

    const normalizedQso = normalizeQso(proxiedQso)

    expect(normalizedQso).toEqual(makeQso())
    expect(() => structuredClone(normalizedQso)).not.toThrow()
  })

  it('removes non-string fields from cached records', () => {
    const cachedRecord = {
      ...makeQso(),
      id: 7,
    } as Qso & { id: number }

    expect(normalizeQso(cachedRecord)).toEqual(makeQso())
  })
})