<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { BAND_MAP, BAND_ORDER, NO_LIST, PREF_LIST, getNoName, getNoRomajiName } from '../awards/jarl'
import type { AjaSlot, AwardResults } from '../types'
import AjaMatrixTable from './AjaMatrixTable.vue'

const props = defineProps<{
  stats: AwardResults
}>()

const { t, locale } = useI18n()

interface StickerMilestone {
  label: string
  target: number
}

const workedBandKeys = computed(() => {
  const bandSet = new Set(Array.from(props.stats.aja.data.values()).map((slot) => slot.BAND))
  return BAND_ORDER.filter((band) => bandSet.has(band))
})

const bandColumns = computed(() => workedBandKeys.value.map((band) => ({
  key: band,
  label: BAND_MAP[band] || band,
})))

function getEntityLabel(no: string): string {
  if (locale.value === 'en') {
    return getNoRomajiName(no)
  }
  return getNoName(no)
}

const matrixRows = computed(() => {
  return Object.keys(NO_LIST)
    .sort()
    .filter((no) => {
      if (no === '1001') return false
      const entity = NO_LIST[no]
      return Boolean(entity && ['city', 'designated city', 'gun', 'ku'].includes(entity.type))
    })
    .map((no) => {
      const entity = NO_LIST[no]
      const prefNo = no.substring(0, 2)
      const pref = PREF_LIST[prefNo]
      const cells: Record<string, AjaSlot | null> = {}

      for (const band of workedBandKeys.value) {
        cells[band] = props.stats.aja.data.get(`${no}:${band}`) || null
      }

      return {
        prefNo,
        prefName: locale.value === 'en' ? pref?.romaji || prefNo : pref?.kanji || prefNo,
        no,
        name: getEntityLabel(no),
        deleted: entity.deleted,
        deletedDate: entity.deleted_date,
        cells,
      }
    })
})

const totalTableRows = computed(() => {
  const { jcc, jcg, ku } = props.stats.aja.byBandType
  const rows = [
    { key: 'jcc', label: 'JCC', values: jcc },
    { key: 'jcg', label: 'JCG', values: jcg },
    { key: 'ku', label: 'Ku', values: ku },
  ]

  return rows.map((row) => ({
    ...row,
    perBand: workedBandKeys.value.map((band) => row.values[band] || 0),
    total: workedBandKeys.value.reduce((sum, band) => sum + (row.values[band] || 0), 0),
  }))
})

const totalRow = computed(() => {
  const perBand = workedBandKeys.value.map((band) => totalTableRows.value.reduce((sum, row) => sum + (row.values[band] || 0), 0))
  return {
    perBand,
    total: perBand.reduce((sum, value) => sum + value, 0),
  }
})

const typeTotals = computed(() => totalTableRows.value.map((row) => ({ label: row.label, total: row.total })))

function computeStickerMilestones(count: number): StickerMilestone[] {
  const milestones: StickerMilestone[] = []

  for (let target = 1500; target <= Math.min(count, 3000); target += 500) {
    milestones.push({ label: 'AJA', target })
  }

  if (count > 3000) {
    for (let target = 3150; target <= count; target += 150) {
      milestones.push({ label: 'AJA', target })
    }
  }

  return milestones
}

function getNextTarget(count: number): number {
  if (count < 1000) return 1000
  if (count < 3000) return Math.floor((count - 1000) / 500 + 1) * 500 + 1000
  return Math.floor((count - 3000) / 150 + 1) * 150 + 3000
}

const stickerMilestones = computed(() => computeStickerMilestones(props.stats.aja.count))
const basicAchieved = computed(() => props.stats.aja.count >= 1000)
const nextTarget = computed(() => getNextTarget(props.stats.aja.count))
</script>

<template>
  <div class="space-y-5">
    <div class="grid gap-4 lg:grid-cols-3">
      <section class="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm">
        <h3 class="text-sm font-semibold tracking-[0.18em] text-slate-500">AJA</h3>
        <div class="mt-3 text-4xl font-semibold text-slate-900">{{ stats.aja.count }}</div>
        <div class="mt-4 flex flex-wrap gap-2">
          <span
            v-for="item in typeTotals"
            :key="item.label"
            class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700"
          >
            {{ item.label }} {{ item.total }}
          </span>
        </div>
      </section>

      <section class="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm">
        <h3 class="text-sm font-semibold tracking-[0.18em] text-slate-500">{{ t('aja.basicAward') }}</h3>
        <div class="mt-3 text-lg font-semibold" :class="basicAchieved ? 'text-emerald-700' : 'text-slate-700'">
          {{ basicAchieved ? t('aja.achievedBasic') : t('aja.notYetBasic') }}
        </div>
      </section>

      <section class="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm">
        <h3 class="text-sm font-semibold tracking-[0.18em] text-slate-500">{{ t('aja.nextTarget') }}</h3>
        <div class="mt-3 text-4xl font-semibold text-slate-900">{{ nextTarget }}</div>
      </section>
    </div>

    <section class="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 class="text-sm font-semibold tracking-[0.18em] text-slate-500">{{ t('aja.stickerMilestones') }}</h3>
          <div class="mt-1 text-xs text-slate-500">{{ t('aja.below3000') }} · {{ t('aja.above3000') }}</div>
        </div>
      </div>
      <div v-if="stickerMilestones.length > 0" class="mt-4 flex flex-wrap gap-2">
        <div
          v-for="milestone in stickerMilestones"
          :key="milestone.target"
          class="flex h-18 w-18 shrink-0 flex-col items-center justify-center rounded-2xl border border-rose-300 bg-rose-50 text-rose-900"
        >
          <div class="text-[11px] font-semibold tracking-[0.18em]">{{ milestone.label }}</div>
          <div class="mt-1 text-lg font-bold leading-none">{{ milestone.target }}</div>
        </div>
      </div>
      <div v-else class="mt-4 text-sm text-slate-600">{{ t('aja.noStickerYet') }}</div>
    </section>

    <section class="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 class="text-sm font-semibold tracking-[0.18em] text-slate-500">{{ t('aja.totalTable') }}</h3>
          <div class="mt-1 text-xs text-slate-500">{{ t('aja.totalByType') }}</div>
        </div>
      </div>

      <div class="mt-4 overflow-x-auto rounded-2xl border border-slate-200">
        <table class="min-w-full border-collapse text-sm">
          <thead>
            <tr class="border-b border-slate-200 bg-slate-50 text-slate-600">
              <th class="px-4 py-3 text-left font-medium">{{ t('stats.band') }}</th>
              <th
                v-for="band in bandColumns"
                :key="band.key"
                class="px-4 py-3 text-center font-medium whitespace-nowrap"
              >
                {{ band.label }}
              </th>
              <th class="px-4 py-3 text-center font-medium">{{ t('aja.total') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in totalTableRows" :key="row.key" class="border-t border-slate-100">
              <td class="px-4 py-3 font-medium text-slate-800">{{ row.label }}</td>
              <td v-for="(value, index) in row.perBand" :key="`${row.key}-${index}`" class="px-4 py-3 text-center text-slate-700">
                {{ value }}
              </td>
              <td class="px-4 py-3 text-center font-semibold text-slate-900">{{ row.total }}</td>
            </tr>
            <tr class="border-t border-slate-200 bg-slate-50 font-semibold text-slate-900">
              <td class="px-4 py-3">{{ t('aja.total') }}</td>
              <td v-for="(value, index) in totalRow.perBand" :key="`total-${index}`" class="px-4 py-3 text-center">
                {{ value }}
              </td>
              <td class="px-4 py-3 text-center">{{ totalRow.total }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="space-y-3">
      <div>
        <h3 class="text-sm font-semibold tracking-[0.18em] text-slate-500">{{ t('aja.matrix') }}</h3>
        <div class="mt-1 text-xs text-slate-500">{{ t('aja.workedBandsOnly') }} · {{ t('aja.deletedRowsHint') }}</div>
      </div>
      <div v-if="bandColumns.length === 0" class="rounded-2xl border border-dashed border-slate-300 p-8 text-center text-slate-500">
        {{ t('aja.noWorkedBands') }}
      </div>
      <AjaMatrixTable v-else :bands="bandColumns" :rows="matrixRows" />
    </section>
  </div>
</template>
