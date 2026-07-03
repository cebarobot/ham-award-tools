import type { Qso, AjaSlot, EntityInfo } from '../types'
import {
  NO_LIST, BAND_ORDER,
  isQslReceived, isInJapan, isAfterDate, isOnOrAfterDate, isEarlierQso,
} from './jarl'

const AJA_SKIP_LIST = new Set(['1001'])

export function computeAja(qsos: Qso[]): {
  data: Map<string, AjaSlot>
  byBandType: { jcc: Record<string, number>; jcg: Record<string, number>; ku: Record<string, number> }
} {
  const data = new Map<string, AjaSlot>()
  const entitySet = new Set<string>()

  for (const qso of qsos) {
    if (!isQslReceived(qso)) continue
    if (!isInJapan(qso)) continue
    if (!qso.CNTY) continue

    const no = qso.CNTY
    if (!(no in NO_LIST)) continue

    if (AJA_SKIP_LIST.has(no)) continue

    const info = NO_LIST[no]
    const noType = info.type

    if (noType === 'designated city' && isOnOrAfterDate(qso.QSO_DATE, info.designated_city_date || '')) {
      continue
    }

    if (info.deleted && isAfterDate(qso.QSO_DATE, info.deleted_date)) {
      continue
    }

    const band = qso.BAND
    if (!BAND_ORDER.includes(band)) continue

    const key = `${no}:${band}`

    if (isEarlierQso(qso, data.get(key) || null)) {
      data.set(key, {
        BAND: band,
        CALL: qso.CALL,
        QSO_DATE: qso.QSO_DATE,
        MODE: qso.MODE,
      })
      entitySet.add(no)
    }
  }

  const byBandType = computeByBandType(data)

  return { data, byBandType }
}

function computeByBandType(data: Map<string, AjaSlot>): {
  jcc: Record<string, number>
  jcg: Record<string, number>
  ku: Record<string, number>
} {
  const jcc: Record<string, number> = {}
  const jcg: Record<string, number> = {}
  const ku: Record<string, number> = {}

  for (const band of BAND_ORDER) {
    jcc[band] = 0
    jcg[band] = 0
    ku[band] = 0
  }

  const entityBandSet = new Set<string>()

  for (const [key] of data) {
    const [no, band] = parseAjaKey(key)
    if (!band) continue

    const entityBand = `${no}:${band}`
    if (entityBandSet.has(entityBand)) continue
    entityBandSet.add(entityBand)

    const info: EntityInfo | undefined = NO_LIST[no]
    if (!info) continue

    const noType = info.type
    if (noType === 'city' || noType === 'designated city') {
      if (band in jcc) jcc[band]++
    } else if (noType === 'gun') {
      if (band in jcg) jcg[band]++
    } else if (noType === 'ku') {
      if (band in ku) ku[band]++
    }
  }

  return { jcc, jcg, ku }
}

function parseAjaKey(key: string): [string, string | null] {
  const idx = key.lastIndexOf(':')
  if (idx === -1) return [key, null]
  return [key.substring(0, idx), key.substring(idx + 1)]
}
