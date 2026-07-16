import noList from '../data/no_list.json'
import prefList from '../data/pref_list.json'
import type { EntityInfo, PrefInfo, Qso, QsoSlot } from '../types'

const noListEntities = Object.fromEntries(
  Object.entries(noList).filter(([key]) => key !== '_meta'),
) as Record<string, EntityInfo>

export const NO_LIST = noListEntities
export const PREF_LIST = prefList as Record<string, PrefInfo>

export const BAND_MAP: Record<string, string> = {
  '160m': '1.9MHz',
  '80m': '3.5MHz',
  '40m': '7MHz',
  '30m': '10MHz',
  '20m': '14MHz',
  '17m': '18MHz',
  '15m': '21MHz',
  '12m': '24MHz',
  '10m': '28MHz',
  '6m': '50MHz',
  '2m': '144MHz',
  '70cm': '430MHz',
  '23cm': '1200MHz',
  '13cm': '2400MHz',
  '6cm': '5600MHz',
}

export const BAND_ORDER = Object.keys(BAND_MAP)

export function isQslReceived(qso: Qso): boolean {
  if (qso.QSL_RCVD === 'Y') return true
  if (qso.EQSL_QSL_RCVD === 'Y') return true
  if (qso.LOTW_QSL_RCVD === 'Y') return true
  return false
}

export function isInJapan(qso: Qso): boolean {
  return qso.DXCC === '339' || qso.DXCC === '177' || qso.DXCC === '192'
}

const OGASAWARA_DXCC = new Set(['177', '192'])
const OGASAWARA_PREF = '10'
const OGASAWARA_CNTY = '10007'

export function applyOgasawaraMapping(qso: Qso): Qso {
  if (!qso.DXCC || !OGASAWARA_DXCC.has(qso.DXCC)) return qso

  return {
    ...qso,
    STATE: OGASAWARA_PREF,
    CNTY: OGASAWARA_CNTY,
  }
}

export function getDistrict(prefNo: string): string {
  const id = parseInt(prefNo, 10)
  if (id === 1) return '8'
  if (id >= 2 && id <= 7) return '7'
  if (id >= 8 && id <= 9) return '0'
  if (id >= 10 && id <= 17) return '1'
  if (id >= 18 && id <= 21) return '2'
  if (id >= 22 && id <= 27) return '3'
  if (id >= 28 && id <= 30) return '9'
  if (id >= 31 && id <= 35) return '4'
  if (id >= 36 && id <= 39) return '5'
  if (id >= 40 && id <= 47) return '6'
  return '?'
}

export function getPrefName(no: string): string {
  if (no in PREF_LIST) {
    return PREF_LIST[no].kanji
  }
  return 'ERROR'
}

export function getPrefRomajiName(no: string): string {
  if (no in PREF_LIST) {
    return PREF_LIST[no].romaji
  }
  return 'ERROR'
}

function gunNameWithSuffix(name: string): string {
  if (name.includes(' (')) {
    return name.replace(' (', '郡 (')
  }
  if (name.includes('支庁')) {
    return name
  }
  return name + '郡'
}

function getNoNameList(no: string): string[] {
  if (!(no in NO_LIST)) return []

  const originName = NO_LIST[no].ja_name
  const name: string[] = [getPrefName(no.substring(0, 2))]

  if (no.length === 4) {
    if (no === '1001') {
      return [originName]
    }
    name.push(originName + '市')
  } else if (no.length === 5) {
    name.push(gunNameWithSuffix(originName))
  } else if (no.length === 6) {
    if (no.substring(0, 4) === '1001') {
      name.push(originName + '区')
    } else {
      const parent = getNoNameList(no.substring(0, 4))
      parent.push(originName + '区')
      return parent
    }
  }

  return name
}

export function getNoName(no: string): string {
  return getNoNameList(no).join(' ')
}

function getNoRomajiNameList(no: string): string[] {
  if (!(no in NO_LIST)) return []

  const originName = NO_LIST[no].name
  const name: string[] = [getPrefRomajiName(no.substring(0, 2))]

  if (no.length === 4) {
    if (no === '1001') {
      return [originName]
    }
    name.push(originName)
  } else if (no.length === 5) {
    name.push(originName)
  } else if (no.length === 6) {
    if (no.substring(0, 4) === '1001') {
      name.push(originName)
    } else {
      const parent = getNoRomajiNameList(no.substring(0, 4))
      parent.push(originName)
      return parent
    }
  }

  return name
}

export function getNoRomajiName(no: string): string {
  return getNoRomajiNameList(no).join(' ')
}

export function isAfterDate(qsoDate: string, entityDate: string): boolean {
  if (!entityDate) return false
  return qsoDate > entityDate
}

export function isOnOrAfterDate(qsoDate: string, entityDate: string): boolean {
  if (!entityDate) return false
  return qsoDate >= entityDate
}

export function isEarlierQso(a: Qso, b: QsoSlot | null): boolean {
  if (!b) return true

  const aStamp = `${a.QSO_DATE}${a.TIME_ON || ''}`
  const bStamp = `${b.QSO_DATE}${b.TIME_ON || ''}`
  return aStamp < bStamp
}

export function formatDateYmd(dateStr: string): string {
  if (!dateStr || dateStr.length !== 8) return dateStr
  return dateStr.substring(0, 4) + '-' + dateStr.substring(4, 6) + '-' + dateStr.substring(6, 8)
}

export function formatEntityNameForAja(no: string): string {
  if (!(no in NO_LIST)) return no

  const nameParts = getNoNameList(no)
  let name: string
  if (nameParts.length > 1) {
    name = nameParts.slice(1).join(' ')
  } else {
    name = nameParts[0]
  }

  const info = NO_LIST[no]
  if (info.deleted && info.deleted_date) {
    name += '*' + formatDateYmd(info.deleted_date)
  } else if (info.type === 'designated city' && info.designated_city_date) {
    name += '*' + formatDateYmd(info.designated_city_date)
  }

  return name
}

export function toQsoSlot(qso: Qso): QsoSlot {
  return {
    CALL: qso.CALL,
    QSO_DATE: qso.QSO_DATE,
    TIME_ON: qso.TIME_ON,
    BAND: qso.BAND,
    MODE: qso.MODE,
  }
}
