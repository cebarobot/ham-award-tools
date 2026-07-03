import type { Qso, QsoSlot } from '../types'
import { NO_LIST } from './jarl'
import { computeJcc } from './jcc'

export function computeWaca(qsos: Qso[]): Record<string, QsoSlot> {
  const jccData = computeJcc(qsos)
  const result: Record<string, QsoSlot> = {}

  for (const no of Object.keys(jccData)) {
    const info = NO_LIST[no]
    if (!info || info.deleted) continue
    result[no] = jccData[no]
  }

  return result
}
