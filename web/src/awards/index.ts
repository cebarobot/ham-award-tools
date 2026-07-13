import type { Qso, AwardResults } from '../types'
import { computeAjd } from './ajd'
import { computeWaja } from './waja'
import { computeJcc } from './jcc'
import { computeJcg } from './jcg'
import { computeAja } from './aja'
import { computeWaca } from './waca'
import { computeWaga } from './waga'
import { computeWapc } from './wapc'
import { computeWcsa } from './wcsa'

export function computeAllAwards(qsos: Qso[]): AwardResults {
  const ajdData = computeAjd(qsos)
  const wajaData = computeWaja(qsos)
  const jccData = computeJcc(qsos)
  const jcgData = computeJcg(qsos)
  const ajaResult = computeAja(qsos)
  const wacaData = computeWaca(qsos)
  const wagaData = computeWaga(qsos)
  const wapcResult = computeWapc(qsos)
  const wcsaResult = computeWcsa(qsos)

  return {
    ajd: ajdData,
    ajdCount: Object.keys(ajdData).length,
    waja: wajaData,
    wajaCount: Object.keys(wajaData).length,
    jcc: { data: jccData, count: Object.keys(jccData).length },
    jcg: { data: jcgData, count: Object.keys(jcgData).length },
    aja: {
      data: ajaResult.data,
      count: ajaResult.data.size,
      byBandType: ajaResult.byBandType,
    },
    waca: { data: wacaData, count: Object.keys(wacaData).length },
    waga: { data: wagaData, count: Object.keys(wagaData).length },
    wapc: wapcResult,
    wcsa: wcsaResult,
  }
}
