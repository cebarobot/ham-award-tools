<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { PREF_LIST, formatDateYmd, getDistrict } from '../awards/jarl'
import type { AwardResults, QsoSlot } from '../types'

const props = defineProps<{
  stats: AwardResults
}>()

const { t, locale } = useI18n()
const DISTRICT_ORDER = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

function formatPercent(worked: number, total: number): string {
  if (total === 0) return '0%'
  return `${Math.round((worked / total) * 100)}%`
}

function slotSummary(slot: QsoSlot | null): string {
  if (!slot) return t('ajdwaja.notWorked')
  return `${slot.CALL}\n${formatDateYmd(slot.QSO_DATE)}\n${slot.BAND} ${slot.MODE}`
}

const ajdAreas = computed(() => {
  return DISTRICT_ORDER.map((no) => {
    return {
      no,
      label: t('ajdwaja.area', { no }),
      slot: props.stats.ajd[no] || null,
    }
  })
})

const wajaGroups = computed(() => {
  const groups: Record<string, Array<{ prefNo: string; name: string; slot: QsoSlot | null }>> = {}

  for (const prefNo of Object.keys(PREF_LIST).sort()) {
    const district = getDistrict(prefNo)
    if (!groups[district]) {
      groups[district] = []
    }

    const pref = PREF_LIST[prefNo]
    groups[district].push({
      prefNo,
      name: locale.value === 'en' ? pref.romaji : pref.kanji,
      slot: props.stats.waja[prefNo] || null,
    })
  }

  return DISTRICT_ORDER
    .filter((district) => district in groups)
    .map((district) => ({
      district,
      label: t('ajdwaja.area', { no: district }),
      items: groups[district],
    }))
})
</script>

<template>
  <div class="space-y-5">
    <section class="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm">
      <h3 class="text-sm font-semibold tracking-[0.18em] text-slate-500">AJD</h3>
      <div class="mt-3 text-3xl font-semibold text-slate-900">{{ stats.ajdCount }} / 10</div>
      <div class="mt-1 text-sm text-slate-500">{{ formatPercent(stats.ajdCount, 10) }}</div>

      <div class="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <div
          v-for="area in ajdAreas"
          :key="area.no"
          class="rounded-2xl border p-3"
          :class="area.slot ? 'border-emerald-200 bg-emerald-50 text-emerald-900' : 'border-slate-200 bg-slate-50 text-slate-600'"
          :title="slotSummary(area.slot)"
        >
          <div class="text-xs font-semibold tracking-[0.18em]">{{ area.label }}</div>
          <div class="mt-3 text-2xl font-bold leading-none">{{ area.no }}</div>
          <template v-if="area.slot">
            <div class="mt-3 text-xs font-medium">{{ area.slot.CALL }}</div>
            <div class="text-xs">{{ formatDateYmd(area.slot.QSO_DATE) }}</div>
            <div class="text-xs">{{ area.slot.BAND }} {{ area.slot.MODE }}</div>
          </template>
          <div v-else class="mt-3 text-xs">{{ t('ajdwaja.notWorked') }}</div>
        </div>
      </div>
    </section>

    <section class="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm">
      <h3 class="text-sm font-semibold tracking-[0.18em] text-slate-500">WAJA</h3>
      <div class="mt-3 text-3xl font-semibold text-slate-900">{{ stats.wajaCount }} / 47</div>
      <div class="mt-1 text-sm text-slate-500">{{ formatPercent(stats.wajaCount, 47) }}</div>

      <div class="mt-4 space-y-4">
        <section v-for="group in wajaGroups" :key="group.district" class="space-y-2">
          <div class="text-xs font-semibold tracking-[0.18em] text-slate-500">{{ group.label }}</div>
          <div class="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
            <div
              v-for="pref in group.items"
              :key="pref.prefNo"
              class="rounded-2xl border p-3"
              :class="pref.slot ? 'border-sky-200 bg-sky-50 text-sky-900' : 'border-slate-200 bg-slate-50 text-slate-600'"
              :title="slotSummary(pref.slot)"
            >
              <div class="flex items-center justify-between gap-2">
                <span class="text-xs font-mono text-slate-500">{{ pref.prefNo }}</span>
                <span class="text-xs font-medium">{{ pref.slot ? t('stats.worked') : t('ajdwaja.notWorked') }}</span>
              </div>
              <div class="mt-2 text-sm font-semibold">{{ pref.name }}</div>
              <template v-if="pref.slot">
                <div class="mt-2 text-xs">{{ pref.slot.CALL }}</div>
                <div class="text-xs">{{ formatDateYmd(pref.slot.QSO_DATE) }}</div>
                <div class="text-xs">{{ pref.slot.BAND }} {{ pref.slot.MODE }}</div>
              </template>
            </div>
          </div>
        </section>
      </div>
    </section>
  </div>
</template>