import type { Qso, QsoSlot } from '../types'
import {
  NO_LIST, isQslReceived, isInJapan, applyOgasawaraMapping, isAfterDate, isEarlierQso, toQsoSlot,
} from './jarl'

export function computeJcc(qsos: Qso[]): Record<string, QsoSlot> {
  const result: Record<string, QsoSlot> = {}

  for (const originQso of qsos) {
    if (!isQslReceived(originQso)) continue
    if (!isInJapan(originQso)) continue
    const qso = applyOgasawaraMapping(originQso)
    if (!qso.CNTY) continue

    const no = qso.CNTY
    if (!(no in NO_LIST)) continue

    const info = NO_LIST[no]
    const noType = info.type

    if (info.deleted && isAfterDate(qso.QSO_DATE, info.deleted_date)) {
      continue
    }

    let targetNo: string
    if (noType === 'city' || noType === 'designated city') {
      targetNo = no
    } else if (noType === 'ku') {
      targetNo = no.substring(0, 4)
    } else {
      continue
    }

    if (isEarlierQso(qso, result[targetNo] || null)) {
      result[targetNo] = toQsoSlot(qso)
    }
  }

  return result
}
