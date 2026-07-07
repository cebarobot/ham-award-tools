import type { Qso, QsoSlot } from '../types'
import { NO_LIST, isQslReceived, isInJapan, isAfterDate, isEarlierQso, toQsoSlot } from './jarl'

export function computeJcg(qsos: Qso[]): Record<string, QsoSlot> {
  const result: Record<string, QsoSlot> = {}

  for (const qso of qsos) {
    if (!isQslReceived(qso)) continue
    if (!isInJapan(qso)) continue
    if (!qso.CNTY) continue

    const no = qso.CNTY
    if (!(no in NO_LIST)) continue

    const info = NO_LIST[no]

    if (info.type !== 'gun') continue

    if (info.deleted && isAfterDate(qso.QSO_DATE, info.deleted_date)) {
      continue
    }

    if (isEarlierQso(qso, result[no] || null)) {
      result[no] = toQsoSlot(qso)
    }
  }

  return result
}
