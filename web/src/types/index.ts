export interface Qso {
  CALL: string
  QSO_DATE: string
  TIME_ON: string
  BAND: string
  MODE: string
  DXCC?: string
  STATE?: string
  CNTY?: string
  QSL_RCVD?: string
  EQSL_QSL_RCVD?: string
  LOTW_QSL_RCVD?: string
  APP_LOTW_MODEGROUP?: string
  GRIDSQUARE?: string
  IOTA?: string
  CQZ?: string
  ITUZ?: string
  CONT?: string
  PROP_MODE?: string
  SAT_NAME?: string
  [key: string]: string | undefined
}

export type EntityType = 'city' | 'designated city' | 'gun' | 'ku'

export interface EntityInfo {
  type: EntityType
  name: string
  ja_name: string
  deleted: boolean
  deleted_date: string
  lat: number
  lon: number
  designated_city?: boolean
  designated_city_date?: string
}

export interface PrefInfo {
  type: 'Prefecture'
  romaji: string
  kanji: string
}

export interface QsoSlot {
  CALL: string
  QSO_DATE: string
  TIME_ON: string
  BAND: string
  MODE: string
}

export interface AjaSlot {
  BAND: string
  CALL: string
  QSO_DATE: string
  TIME_ON: string
  MODE: string
}

export interface JccJcgResult {
  data: Record<string, QsoSlot>
  count: number
}

export interface AjaResult {
  data: Map<string, AjaSlot>
  count: number
  byBandType: {
    jcc: Record<string, number>
    jcg: Record<string, number>
    ku: Record<string, number>
  }
}

export interface WapcResult {
  mixed: Record<string, QsoSlot | null>
  band: Record<string, Record<string, QsoSlot | null>>
  mode: Record<string, Record<string, QsoSlot | null>>
  mixedCount: number
  bandCounts: Record<string, number>
  modeCounts: Record<string, number>
}

export interface WcsaSlot {
  schoolCall: string
  schoolName: string
  qso: QsoSlot & {
    PROP_MODE: string
    SAT_NAME: string
  }
}

export interface WcsaLevel {
  name: 'Bronze' | 'Silver' | 'Gold'
  requiredSchools: number
  requiredSlots: number
  achieved: boolean
}

export interface WcsaResult {
  slots: Map<string, WcsaSlot>
  schoolCount: number
  slotCount: number
  levels: WcsaLevel[]
  slotCountsBySchool: Record<string, number>
}

export interface AwardResults {
  ajd: Record<string, QsoSlot>
  ajdCount: number
  waja: Record<string, QsoSlot>
  wajaCount: number
  jcc: JccJcgResult
  jcg: JccJcgResult
  aja: AjaResult
  waca: JccJcgResult
  waga: JccJcgResult
  wapc: WapcResult
  wcsa: WcsaResult
}
