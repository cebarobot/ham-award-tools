import { AdifParser } from 'adif-parser-ts'
import type { Qso } from '../types'

const KNOWN_FIELDS = new Set([
  'CALL', 'QSO_DATE', 'TIME_ON', 'BAND', 'MODE',
  'DXCC', 'STATE', 'CNTY',
  'QSL_RCVD', 'EQSL_QSL_RCVD', 'LOTW_QSL_RCVD',
  'APP_LOTW_MODEGROUP', 'GRIDSQUARE', 'IOTA', 'CQZ', 'ITUZ', 'CONT',
  'PROP_MODE', 'SAT_NAME',
])

export function parseAdifText(text: string): Qso[] {
  const parsed = AdifParser.parseAdi(text)
  if (!parsed.records) return []

  return parsed.records.map((rec) => {
    const qso = {} as Record<string, string>
    for (const [key, value] of Object.entries(rec)) {
      const upperKey = key.toUpperCase()
      if (KNOWN_FIELDS.has(upperKey)) {
        qso[upperKey] = value
      } else {
        qso[upperKey] = value
      }
    }
    return qso as Qso
  })
}

export function parseAdifFile(file: File): Promise<Qso[]> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      try {
        const qsos = parseAdifText(reader.result as string)
        resolve(qsos)
      } catch (e) {
        reject(e)
      }
    }
    reader.onerror = () => reject(reader.error)
    reader.readAsText(file)
  })
}
