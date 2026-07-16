import type { Qso, QsoSlot } from '../types'
import { isQslReceived, isInJapan, applyOgasawaraMapping, getDistrict, isEarlierQso, toQsoSlot } from './jarl'

export function computeWaja(qsos: Qso[]): Record<string, QsoSlot> {
  const result: Record<string, QsoSlot> = {}

  for (const originQso of qsos) {
    if (!isQslReceived(originQso)) continue
    if (!isInJapan(originQso)) continue
    const qso = applyOgasawaraMapping(originQso)
    if (!qso.STATE) continue

    const pref = qso.STATE
    const callChar = qso.CALL.startsWith('J') ? qso.CALL[2] : '1'
    const district = getDistrict(pref)

    if (callChar !== district) continue

    if (isEarlierQso(qso, result[pref] || null)) {
      result[pref] = toQsoSlot(qso)
    }
  }

  return result
}
