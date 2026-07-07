import type { Qso, QsoSlot, WapcResult } from '../types'
import { toQsoSlot } from './jarl'

const DXCC_CHINA = '318'
const DXCC_OTHER: Record<string, string> = {
  '386': 'TW',
  '321': 'HK',
  '152': 'MO',
}

const PROVINCES = [
  'BJ', 'HL', 'JL', 'LN', 'TJ', 'NM', 'HE', 'SX', 'SH', 'SD',
  'JS', 'ZJ', 'JX', 'FJ', 'AH', 'HA', 'HB', 'HN', 'GD', 'GX',
  'HI', 'SC', 'CQ', 'GZ', 'YN', 'SN', 'GS', 'NX', 'QH', 'XJ',
  'XZ', 'TW', 'HK', 'MO',
]

const BANDS = ['160m', '80m', '40m', '30m', '20m', '17m', '15m', '12m', '10m'] as const

const MODES = ['CW', 'PHONE', 'DATA'] as const
type WapcModeGroup = (typeof MODES)[number]

const ROOT_MODE_GROUPS: Record<string, WapcModeGroup> = {
  AM: 'PHONE',
  CW: 'CW',
  DIGITALVOICE: 'PHONE',
  FM: 'PHONE',
  SSB: 'PHONE',
  VOI: 'PHONE',
}

function initSlots(): Record<string, QsoSlot | null> {
  const slots: Record<string, QsoSlot | null> = {}
  for (const p of PROVINCES) slots[p] = null
  return slots
}

function initSlotsNested(list: readonly string[]): Record<string, Record<string, QsoSlot | null>> {
  const slots: Record<string, Record<string, QsoSlot | null>> = {}
  for (const p of PROVINCES) {
    slots[p] = {}
    for (const x of list) {
      slots[p][x] = null
    }
  }
  return slots
}

export function computeWapc(qsos: Qso[]): WapcResult {
  const mixed = initSlots()
  const band = initSlotsNested(BANDS)
  const mode = initSlotsNested(MODES)

  for (const qso of qsos) {
    if (!qso.DXCC) continue

    let province: string | null = null

    if (qso.DXCC === DXCC_CHINA && qso.STATE) {
      province = qso.STATE.toUpperCase()
    } else if (qso.DXCC in DXCC_OTHER) {
      province = DXCC_OTHER[qso.DXCC]
    }

    if (!province || !PROVINCES.includes(province)) continue

    const slotBand = qso.BAND.toLowerCase()
    const slotMode = qso.MODE.toUpperCase()
    const modeGroup = ROOT_MODE_GROUPS[slotMode] || 'DATA'
    const slot: QsoSlot = {
      ...toQsoSlot(qso),
      BAND: slotBand,
      MODE: slotMode,
    }

    if (!mixed[province]) {
      mixed[province] = slot
    }

    if (BANDS.includes(slotBand as (typeof BANDS)[number]) && !band[province][slotBand]) {
      band[province][slotBand] = slot
    }

    if (!mode[province][modeGroup]) {
      mode[province][modeGroup] = slot
    }
  }

  let mixedCount = 0
  const bandCounts: Record<string, number> = {}
  const modeCounts: Record<string, number> = {}

  for (const b of BANDS) bandCounts[b] = 0
  for (const m of MODES) modeCounts[m] = 0

  for (const p of PROVINCES) {
    if (mixed[p]) mixedCount++
    for (const b of BANDS) {
      if (band[p][b]) bandCounts[b]++
    }
    for (const m of MODES) {
      if (mode[p][m]) modeCounts[m]++
    }
  }

  return { mixed, band, mode, mixedCount, bandCounts, modeCounts }
}
