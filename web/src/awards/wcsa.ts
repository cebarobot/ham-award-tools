import schoolList from '../data/wcsa.json'
import type { Qso, WcsaLevel, WcsaResult, WcsaSlot } from '../types'

const SCHOOLS = Object.fromEntries(
  Object.entries(schoolList).map(([call, name]) => [call.toUpperCase(), String(name)]),
) as Record<string, string>

const AWARD_LEVELS: Array<{ name: WcsaLevel['name']; requiredSchools: number; requiredSlots: number }> = [
  { name: 'Bronze', requiredSchools: 1, requiredSlots: 3 },
  { name: 'Silver', requiredSchools: 2, requiredSlots: 6 },
  { name: 'Gold', requiredSchools: 3, requiredSlots: 10 },
]

function isWcsaQslReceived(qso: Qso): boolean {
  if (qso.QSL_RCVD?.toUpperCase() === 'Y') return true
  if (qso.LOTW_QSL_RCVD?.toUpperCase() === 'Y') return true
  return false
}

function normalizeQso(qso: Qso): Qso {
  const normalized: Record<string, string> = {}
  for (const [key, value] of Object.entries(qso)) {
    normalized[key.toUpperCase()] = value === undefined ? '' : String(value).trim()
  }

  for (const key of ['CALL', 'MODE', 'PROP_MODE', 'SAT_NAME']) {
    if (normalized[key]) normalized[key] = normalized[key].toUpperCase()
  }

  return normalized as Qso
}

function getSchoolCall(call: string): string | null {
  const normalizedCall = call.trim().toUpperCase()
  if (normalizedCall in SCHOOLS) return normalizedCall

  for (const part of normalizedCall.split('/')) {
    if (part in SCHOOLS) return part
  }

  return null
}

function getSlotKey(qso: Qso): string | null {
  const call = qso.CALL?.toUpperCase() || ''
  const mode = qso.MODE?.toUpperCase() || ''
  const propMode = qso.PROP_MODE?.toUpperCase() || ''

  if (!call || !qso.QSO_DATE || !mode) return null

  if (propMode === 'SAT') {
    const satName = qso.SAT_NAME?.toUpperCase() || ''
    if (!satName) return null
    return [call, 'SAT', satName, mode].join('|')
  }

  const band = qso.BAND?.toUpperCase() || ''
  if (!band) return null

  if (propMode === 'EME' || propMode === 'MS') {
    return [call, band, mode, propMode].join('|')
  }

  return [call, band, mode].join('|')
}

function qsoStamp(qso: Pick<Qso, 'QSO_DATE' | 'TIME_ON'>): string {
  return `${qso.QSO_DATE || ''}${qso.TIME_ON || ''}`
}

function toWcsaSlot(schoolCall: string, qso: Qso): WcsaSlot {
  return {
    schoolCall,
    schoolName: SCHOOLS[schoolCall],
    qso: {
      CALL: qso.CALL,
      QSO_DATE: qso.QSO_DATE,
      TIME_ON: qso.TIME_ON || '',
      BAND: qso.BAND || '',
      MODE: qso.MODE,
      PROP_MODE: qso.PROP_MODE || '',
      SAT_NAME: qso.SAT_NAME || '',
    },
  }
}

function buildResult(slots: Map<string, WcsaSlot>): WcsaResult {
  const schoolCalls = Array.from(new Set(Array.from(slots.values()).map((slot) => slot.schoolCall))).sort()
  const slotCountsBySchool: Record<string, number> = {}
  for (const schoolCall of schoolCalls) slotCountsBySchool[schoolCall] = 0
  for (const slot of slots.values()) slotCountsBySchool[slot.schoolCall]++

  const schoolCount = schoolCalls.length
  const slotCount = slots.size
  const levels = AWARD_LEVELS.map((level) => ({
    ...level,
    achieved: schoolCount >= level.requiredSchools && slotCount >= level.requiredSlots,
  }))

  return {
    slots,
    schoolCount,
    slotCount,
    levels,
    slotCountsBySchool,
  }
}

export function computeWcsa(qsos: Qso[]): WcsaResult {
  const slots = new Map<string, WcsaSlot>()

  for (const qso of qsos) {
    const normalizedQso = normalizeQso(qso)
    const schoolCall = getSchoolCall(normalizedQso.CALL || '')

    if (!schoolCall) continue
    if (!isWcsaQslReceived(normalizedQso)) continue

    const slotKey = getSlotKey(normalizedQso)
    if (!slotKey) continue

    const existing = slots.get(slotKey)
    if (!existing || qsoStamp(normalizedQso) < qsoStamp(existing.qso)) {
      slots.set(slotKey, toWcsaSlot(schoolCall, normalizedQso))
    }
  }

  return buildResult(slots)
}
