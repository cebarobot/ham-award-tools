import type { Qso, QsoSlot } from '../types'
import { NO_LIST, isQslReceived, isInJapan, isAfterDate, isEarlierQso } from './jarl'

export function computeJcc(qsos: Qso[]): Record<string, QsoSlot> {
  const result: Record<string, QsoSlot> = {}

  for (const qso of qsos) {
    if (!isQslReceived(qso)) continue
    if (!isInJapan(qso)) continue
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
      result[targetNo] = {
        CALL: qso.CALL,
        QSO_DATE: qso.QSO_DATE,
        BAND: qso.BAND,
        MODE: qso.MODE,
      }
    }
  }

  return result
}
