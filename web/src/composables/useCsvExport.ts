import type { AwardResults, QsoSlot, AjaSlot } from '../types'
import { NO_LIST, BAND_ORDER, getNoName, getPrefName, formatEntityNameForAja } from '../awards/jarl'

const QSL_HEADER = 'No.,Callsign,Date,Band,Mode,Remarks'
const AJA_HEADER = 'City/Gun/Ku,Band,Callsign,Date,Mode,Remarks'

function csvEscape(value: string): string {
  if (value.includes(',') || value.includes('"') || value.includes('\n')) {
    return `"${value.replace(/"/g, '""')}"`
  }
  return value
}

function makeCsv(headers: string[], rows: string[][]): string {
  const bom = '\uFEFF'
  const lines = [headers.join(','), ...rows.map((row) => row.map(csvEscape).join(','))]
  return bom + lines.join('\n') + '\n'
}

function qslRow(idx: number, slot: QsoSlot | null, remarks: string): string[] {
  if (slot) {
    return [String(idx), slot.CALL, slot.QSO_DATE, slot.BAND, slot.MODE, remarks]
  }
  return [String(idx), '', '', '', '', remarks]
}

export function generateAjdCsv(results: AwardResults): string {
  const rows: string[][] = []
  let idx = 1
  for (let d = 0; d < 10; d++) {
    const district = String(d)
    rows.push(qslRow(idx, results.ajd[district] || null, `Area ${d}`))
    idx++
  }
  return makeCsv(QSL_HEADER.split(','), rows)
}

export function generateWajaCsv(results: AwardResults): string {
  const rows: string[][] = []
  let idx = 1
  for (let d = 1; d <= 47; d++) {
    const pref = String(d).padStart(2, '0')
    rows.push(qslRow(idx, results.waja[pref] || null, `${pref} ${getPrefName(pref)}`))
    idx++
  }
  return makeCsv(QSL_HEADER.split(','), rows)
}

export function generateJccCsv(results: AwardResults): string {
  const rows: string[][] = []
  let idx = 1
  const keys = Object.keys(results.jcc.data).sort()
  for (const no of keys) {
    const info = NO_LIST[no]
    const mark = info?.deleted ? ' *' : ''
    rows.push(qslRow(idx, results.jcc.data[no], `${no} ${getNoName(no)}${mark}`))
    idx++
  }
  return makeCsv(QSL_HEADER.split(','), rows)
}

export function generateJcgCsv(results: AwardResults): string {
  const rows: string[][] = []
  let idx = 1
  const keys = Object.keys(results.jcg.data).sort()
  for (const no of keys) {
    const info = NO_LIST[no]
    const mark = info?.deleted ? ' *' : ''
    rows.push(qslRow(idx, results.jcg.data[no], `${no} ${getNoName(no)}${mark}`))
    idx++
  }
  return makeCsv(QSL_HEADER.split(','), rows)
}

export function generateAjaCsv(results: AwardResults): string {
  const rows: string[][] = []
  const entries = Array.from(results.aja.data.entries())
  entries.sort(([a], [b]) => a.localeCompare(b))

  for (const [key, slot] of entries) {
    const no = key.split(':')[0]
    const info = NO_LIST[no]
    const mark = info?.deleted ? ' *' : ''
    rows.push([no, slot.BAND, slot.CALL, slot.QSO_DATE, slot.MODE, `${getNoName(no)}${mark}`])
  }
  return makeCsv(AJA_HEADER.split(','), rows)
}

export function generateAjaListCsv(results: AwardResults): string {
  const rows: string[][] = []
  const freqLabels = BAND_ORDER.map((b) => BAND_ORDER.includes(b) ? BAND_ORDER.includes(b) : b)

  const header1 = ['', 'JCC/JCG/Ku', '', '', ...freqLabels.flatMap((f) => [f, ''])]
  const header2 = ['', 'Name', '', 'Number', ...BAND_ORDER.flatMap(() => ['Mode', 'Callsign'])]
  const header3 = ['', '', '', '', ...BAND_ORDER.flatMap(() => ['check', 'Date'])]

  rows.push(header1)
  rows.push(header2)
  rows.push(header3)

  let lastPref = ''
  const entityNos = Object.keys(NO_LIST)
  for (const no of entityNos) {
    if (no === '_meta') continue
    const info = NO_LIST[no]
    if (!info || !['city', 'designated city', 'gun', 'ku'].includes(info.type)) continue
    if (no === '1001') continue // AJA_SKIP_LIST

    const thisPref = no.substring(0, 2)
    const prefCol = thisPref !== lastPref ? getPrefName(thisPref) + ' ' + thisPref : ''
    lastPref = thisPref

    const entityName = formatEntityNameForAja(no)

    const row1Bands: string[] = []
    const row2Bands: string[] = []
    for (const band of BAND_ORDER) {
      const key = `${no}:${band}`
      const slot = results.aja.data.get(key)
      if (slot) {
        row1Bands.push(slot.MODE, slot.CALL)
        row2Bands.push('', slot.QSO_DATE)
      } else {
        row1Bands.push('', '')
        row2Bands.push('', '')
      }
    }

    rows.push(['', prefCol, entityName, no, ...row1Bands])
    rows.push(['', '', '', '', ...row2Bands])
  }

  return '\uFEFF' + rows.map((row) => row.map(csvEscape).join(',')).join('\n') + '\n'
}

export function generateAjaTotalTableCsv(results: AwardResults): string {
  const { jcc, jcg, ku } = results.aja.byBandType

  const header = ['Band', ...BAND_ORDER.map((b) => BAND_ORDER.find((x) => x === b) || b), 'Total']
  const jccRow = ['JCC', ...BAND_ORDER.map((b) => String(jcc[b] || 0)), String(Object.values(jcc).reduce((a, b) => a + b, 0))]
  const jcgRow = ['JCG', ...BAND_ORDER.map((b) => String(jcg[b] || 0)), String(Object.values(jcg).reduce((a, b) => a + b, 0))]
  const kuRow = ['Ku', ...BAND_ORDER.map((b) => String(ku[b] || 0)), String(Object.values(ku).reduce((a, b) => a + b, 0))]

  const totalPerBand = BAND_ORDER.map((b, i) => {
    return Number(jccRow[i + 1]) + Number(jcgRow[i + 1]) + Number(kuRow[i + 1])
  })
  const totalRow = ['Total', ...totalPerBand.map(String), String(totalPerBand.reduce((a, b) => a + b, 0))]

  return makeCsv(header, [jccRow, jcgRow, kuRow, totalRow])
}

const BANDS_WAPC = ['160M', '80M', '40M', '30M', '20M', '17M', '15M', '12M', '10M']
const MODES_WAPC = ['CW', 'PHONE', 'DATA']

export function generateWapcBandCsv(results: AwardResults): string {
  const header = ['Province', 'MIXED', ...BANDS_WAPC]
  const rows: string[][] = []
  const provinces = Object.keys(results.wapc.mixed).sort()

  for (const p of provinces) {
    const row = [p]
    row.push(results.wapc.mixed[p]?.CALL || '')
    for (const b of BANDS_WAPC) {
      row.push(results.wapc.band[p]?.[b]?.CALL || '')
    }
    rows.push(row)
  }

  return makeCsv(header, rows)
}

export function generateWapcModeCsv(results: AwardResults): string {
  const header = ['Province', ...MODES_WAPC]
  const rows: string[][] = []
  const provinces = Object.keys(results.wapc.mixed).sort()

  for (const p of provinces) {
    const row = [p]
    for (const m of MODES_WAPC) {
      row.push(results.wapc.mode[p]?.[m]?.CALL || '')
    }
    rows.push(row)
  }

  return makeCsv(header, rows)
}

export function downloadCsv(filename: string, content: string): void {
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export function useCsvExport() {
  return {
    generateAjdCsv,
    generateWajaCsv,
    generateJccCsv,
    generateJcgCsv,
    generateAjaCsv,
    generateAjaListCsv,
    generateAjaTotalTableCsv,
    generateWapcBandCsv,
    generateWapcModeCsv,
    downloadCsv,
  }
}
