<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { formatDateYmd } from '../awards/jarl'
import type { AjaSlot } from '../types'

interface BandColumn {
  key: string
  label: string
}

interface AjaMatrixRow {
  prefNo: string
  prefName: string
  no: string
  name: string
  deleted: boolean
  deletedDate?: string
  cells: Record<string, AjaSlot | null>
}

const props = defineProps<{
  bands: BandColumn[]
  rows: AjaMatrixRow[]
}>()

const { t } = useI18n()

function titleForCell(row: AjaMatrixRow, bandKey: string): string {
  const slot = row.cells[bandKey]
  const lines = [`${row.no} ${row.name}`]

  if (row.deleted && row.deletedDate) {
    lines.push(`${t('jccjcg.deleted')} ${formatDateYmd(row.deletedDate)}`)
  }

  if (!slot) {
    lines.push(t('jccjcg.notWorked'))
    return lines.join('\n')
  }

  lines.push(slot.CALL)
  lines.push(formatDateYmd(slot.QSO_DATE))
  lines.push(`${bandKey} ${slot.MODE}`)
  return lines.join('\n')
}
</script>

<template>
  <div class="overflow-x-auto rounded-2xl border border-slate-200 bg-white/90 shadow-sm">
    <table class="min-w-full border-collapse text-sm">
      <thead>
        <tr class="border-b border-slate-200 bg-slate-50 text-slate-600">
          <th class="sticky left-0 z-10 bg-slate-50 px-3 py-3 text-left font-medium">{{ t('aja.prefecture') }}</th>
          <th class="sticky left-[5.5rem] z-10 bg-slate-50 px-3 py-3 text-left font-medium">{{ t('aja.entity') }}</th>
          <th class="sticky left-[18rem] z-10 bg-slate-50 px-3 py-3 text-left font-medium">{{ t('aja.number') }}</th>
          <th
            v-for="band in bands"
            :key="band.key"
            class="px-3 py-3 text-center font-medium whitespace-nowrap"
          >
            {{ band.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="row in rows"
          :key="row.no"
          :class="row.deleted ? 'deleted-row' : 'border-t border-slate-100'"
        >
          <td class="sticky left-0 z-10 px-3 py-2.5 text-xs font-medium text-slate-500 bg-white/95 whitespace-nowrap">
            {{ row.prefNo }} {{ row.prefName }}
          </td>
          <td class="sticky left-[5.5rem] z-10 px-3 py-2.5 text-slate-800 bg-white/95 min-w-[12.5rem]">
            <div class="font-medium">{{ row.name }}</div>
            <div v-if="row.deleted && row.deletedDate" class="text-xs text-amber-700">
              {{ formatDateYmd(row.deletedDate) }}
            </div>
          </td>
          <td class="sticky left-[18rem] z-10 px-3 py-2.5 font-mono text-xs text-slate-500 bg-white/95 whitespace-nowrap">
            {{ row.no }}
          </td>
          <td
            v-for="band in bands"
            :key="`${row.no}-${band.key}`"
            class="px-3 py-2.5 text-center"
          >
            <div
              class="mx-auto h-6 w-6 rounded-md border"
              :class="row.cells[band.key]
                ? 'border-emerald-600 bg-emerald-500'
                : 'border-slate-300 bg-white'"
              :title="titleForCell(row, band.key)"
            />
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.deleted-row td {
  background-image: repeating-linear-gradient(
    -45deg,
    rgba(245, 158, 11, 0.05),
    rgba(245, 158, 11, 0.05) 6px,
    rgba(245, 158, 11, 0.12) 6px,
    rgba(245, 158, 11, 0.12) 12px
  );
  border-top: 1px solid rgb(254 243 199);
}
</style>