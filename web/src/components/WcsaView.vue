<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { formatDateYmd } from '../awards/jarl'
import type { AwardResults, WcsaSlot } from '../types'

const props = defineProps<{
  stats: AwardResults
}>()

const { t } = useI18n()

const levels = computed(() => props.stats.wcsa.levels)

const schoolRows = computed(() => {
  const firstSlotsBySchool = new Map<string, WcsaSlot>()
  for (const slot of props.stats.wcsa.slots.values()) {
    if (!firstSlotsBySchool.has(slot.schoolCall)) firstSlotsBySchool.set(slot.schoolCall, slot)
  }

  return Object.entries(props.stats.wcsa.slotCountsBySchool)
    .map(([schoolCall, count]) => ({
      schoolCall,
      schoolName: firstSlotsBySchool.get(schoolCall)?.schoolName || schoolCall,
      count,
    }))
    .sort((a, b) => a.schoolCall.localeCompare(b.schoolCall))
})

const slotRows = computed(() => Array.from(props.stats.wcsa.slots.values()).sort((a, b) => {
  const aKey = `${a.schoolCall}|${a.qso.QSO_DATE}|${a.qso.TIME_ON}|${a.qso.BAND}|${a.qso.MODE}|${a.qso.PROP_MODE}|${a.qso.SAT_NAME}`
  const bKey = `${b.schoolCall}|${b.qso.QSO_DATE}|${b.qso.TIME_ON}|${b.qso.BAND}|${b.qso.MODE}|${b.qso.PROP_MODE}|${b.qso.SAT_NAME}`
  return aKey.localeCompare(bKey)
}))

function formatProp(slot: WcsaSlot): string {
  if (slot.qso.PROP_MODE === 'SAT') return `${slot.qso.PROP_MODE} ${slot.qso.SAT_NAME}`.trim()
  return slot.qso.PROP_MODE || '-'
}
</script>

<template>
  <div class="space-y-5">
    <div class="grid gap-4 lg:grid-cols-5">
      <section class="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm lg:col-span-2">
        <h3 class="text-sm font-semibold tracking-[0.18em] text-slate-500">{{ t('awards.wcsa') }}</h3>
        <div class="mt-4 grid grid-cols-2 gap-3">
          <div class="rounded-xl bg-slate-50 p-3">
            <div class="text-2xl font-semibold text-slate-900">{{ stats.wcsa.schoolCount }}</div>
            <div class="mt-1 text-xs text-slate-500">{{ t('wcsa.schools') }}</div>
          </div>
          <div class="rounded-xl bg-slate-50 p-3">
            <div class="text-2xl font-semibold text-slate-900">{{ stats.wcsa.slotCount }}</div>
            <div class="mt-1 text-xs text-slate-500">{{ t('wcsa.slots') }}</div>
          </div>
        </div>
      </section>

      <section
        v-for="level in levels"
        :key="level.name"
        class="rounded-2xl border p-5 shadow-sm"
        :class="level.achieved ? 'border-emerald-200 bg-emerald-50 text-emerald-950' : 'border-slate-200 bg-white/90 text-slate-700'"
      >
        <div class="flex items-center justify-between gap-3">
          <h3 class="text-sm font-semibold tracking-[0.18em] text-slate-500">{{ t(`wcsa.levels.${level.name.toLowerCase()}`) }}</h3>
          <span
            v-if="level.achieved"
            class="rounded-full bg-emerald-600 px-2 py-0.5 text-xs font-semibold text-white"
          >
            OK
          </span>
        </div>
        <div class="mt-4 space-y-1 text-sm">
          <div>{{ t('wcsa.schools') }} {{ stats.wcsa.schoolCount }} / {{ level.requiredSchools }}</div>
          <div>{{ t('wcsa.slots') }} {{ stats.wcsa.slotCount }} / {{ level.requiredSlots }}</div>
        </div>
      </section>
    </div>

    <section class="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm">
      <h3 class="text-sm font-semibold tracking-[0.18em] text-slate-500">{{ t('wcsa.schoolSlots') }}</h3>
      <div class="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="school in schoolRows"
          :key="school.schoolCall"
          class="rounded-xl border border-slate-200 bg-slate-50 p-3"
        >
          <div class="flex items-center justify-between gap-3">
            <span class="font-mono text-sm font-semibold text-slate-800">{{ school.schoolCall }}</span>
            <span class="rounded-full bg-slate-200 px-2 py-0.5 text-xs font-semibold text-slate-700">{{ school.count }} {{ t('wcsa.slots') }}</span>
          </div>
          <div class="mt-2 text-sm text-slate-700">{{ school.schoolName }}</div>
        </div>
      </div>
    </section>

    <section class="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm">
      <h3 class="text-sm font-semibold tracking-[0.18em] text-slate-500">{{ t('wcsa.slotDetails') }}</h3>
      <div class="mt-4 overflow-x-auto rounded-2xl border border-slate-200">
        <table class="min-w-full border-collapse text-sm">
          <thead>
            <tr class="border-b border-slate-200 bg-slate-50 text-slate-600">
              <th class="px-4 py-3 text-left font-medium">{{ t('wcsa.schoolCall') }}</th>
              <th class="px-4 py-3 text-left font-medium">{{ t('wcsa.schoolName') }}</th>
              <th class="px-4 py-3 text-left font-medium">{{ t('wcsa.callsign') }}</th>
              <th class="px-4 py-3 text-left font-medium">{{ t('wcsa.date') }}</th>
              <th class="px-4 py-3 text-left font-medium">{{ t('wcsa.band') }}</th>
              <th class="px-4 py-3 text-left font-medium">{{ t('wcsa.mode') }}</th>
              <th class="px-4 py-3 text-left font-medium">{{ t('wcsa.propagation') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="slot in slotRows" :key="`${slot.qso.CALL}-${slot.qso.BAND}-${slot.qso.MODE}-${slot.qso.PROP_MODE}-${slot.qso.SAT_NAME}`" class="border-t border-slate-100">
              <td class="px-4 py-3 font-mono text-xs text-slate-700">{{ slot.schoolCall }}</td>
              <td class="px-4 py-3 text-slate-800 whitespace-nowrap">{{ slot.schoolName }}</td>
              <td class="px-4 py-3 font-mono text-xs text-slate-700">{{ slot.qso.CALL }}</td>
              <td class="px-4 py-3 text-slate-700 whitespace-nowrap">{{ formatDateYmd(slot.qso.QSO_DATE) }}</td>
              <td class="px-4 py-3 text-slate-700">{{ slot.qso.BAND || '-' }}</td>
              <td class="px-4 py-3 text-slate-700">{{ slot.qso.MODE }}</td>
              <td class="px-4 py-3 text-slate-700 whitespace-nowrap">{{ formatProp(slot) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>
