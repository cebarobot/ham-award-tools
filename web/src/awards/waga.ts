import type { Qso, QsoSlot } from '../types'
import { NO_LIST } from './jarl'
import { computeJcg } from './jcg'

export function computeWaga(qsos: Qso[]): Record<string, QsoSlot> {
  const jcgData = computeJcg(qsos)
  const result: Record<string, QsoSlot> = {}

  for (const no of Object.keys(jcgData)) {
    const info = NO_LIST[no]
    if (!info || info.deleted) continue
    result[no] = jcgData[no]
  }

  return result
}
