<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { AwardResults, EntityInfo, QsoSlot } from '../types'
import { NO_LIST, PREF_LIST } from '../awards/jarl'
import PrefectureBlock from './PrefectureBlock.vue'

type GroupEntry = { no: string; entity: EntityInfo; qso: QsoSlot | null }
type GroupMap = Record<string, GroupEntry[]>

const props = defineProps<{
  stats: AwardResults
}>()

const { t } = useI18n()
const showDeleted = ref(false)
const activeTab = ref<'jcc' | 'jcg'>('jcc')

const jccEntityGroups = computed(() => buildGroups('JCC'))
const jcgEntityGroups = computed(() => buildGroups('JCG'))

function buildGroups(type: 'JCC' | 'JCG'): GroupMap {
  const groups: GroupMap = {}
  const dataMap = type === 'JCC' ? props.stats.jcc.data : props.stats.jcg.data

  const entityNos = Object.keys(NO_LIST).sort()
  for (const no of entityNos) {
    const entity = NO_LIST[no]
    if (!entity) continue

    const matchJcc = type === 'JCC' && ['city', 'designated city'].includes(entity.type)
    const matchJcg = type === 'JCG' && entity.type === 'gun'
    if (!matchJcc && !matchJcg) continue

    const prefNo = no.substring(0, 2)
    if (!(prefNo in PREF_LIST)) continue

    if (!groups[prefNo]) {
      groups[prefNo] = []
    }

    const qso = dataMap[no] || null
    groups[prefNo].push({ no, entity, qso })
  }

  return groups
}

function getAwardLevels(count: number, type: 'jcc' | 'jcg'): string[] {
  if (type === 'jcc') {
    const levels = [100, 200, 300, 400, 500, 600, 700, 800]
    return levels.filter((l) => count >= l).map((l) => `${l}`)
  } else {
    const levels = [100, 200, 300, 400, 500]
    return levels.filter((l) => count >= l).map((l) => `${l}`)
  }
}

const jccAwardLevels = computed(() => getAwardLevels(props.stats.jcc.count, 'jcc'))
const jcgAwardLevels = computed(() => getAwardLevels(props.stats.jcg.count, 'jcg'))

function totalNonDeleted(type: 'city' | 'gun'): number {
  let c = 0
  for (const key of Object.keys(NO_LIST)) {
    if (key === '_meta') continue
    const entity = NO_LIST[key]
    if (!entity || entity.deleted) continue
    if (type === 'city' && ['city', 'designated city'].includes(entity.type)) c++
    if (type === 'gun' && entity.type === 'gun') c++
  }
  return c
}

const wacaWorked = computed(() => props.stats.waca.count)
const wacaTotal = computed(() => totalNonDeleted('city'))
const wagaWorked = computed(() => props.stats.waga.count)
const wagaTotal = computed(() => totalNonDeleted('gun'))

const activePrefectures = computed(() => {
  const groups = activeTab.value === 'jcc' ? jccEntityGroups.value : jcgEntityGroups.value
  return Object.keys(groups).sort()
})

const wacaWidth = computed(() => `${wacaTotal.value > 0 ? (wacaWorked.value / wacaTotal.value) * 100 : 0}%`)
const wagaWidth = computed(() => `${wagaTotal.value > 0 ? (wagaWorked.value / wagaTotal.value) * 100 : 0}%`)

function formatPercent(worked: number, total: number): string {
  if (total === 0) return '0%'
  return `${((worked / total) * 100).toFixed(1)}%`
}

const legendItems = computed(() => [
  {
    key: 'worked',
    label: t('stats.worked'),
    classes: 'border-emerald-600 bg-emerald-500',
  },
  {
    key: 'notWorked',
    label: t('jccjcg.notWorked'),
    classes: 'border-slate-300 bg-white',
  },
  {
    key: 'deleted',
    label: t('jccjcg.deleted'),
    classes: 'border-slate-300 bg-slate-100 striped',
  },
  {
    key: 'workedDeleted',
    label: t('jccjcg.workedDeleted'),
    classes: 'border-emerald-400 bg-emerald-200 striped',
  },
])
</script>

<template>
  <div class="space-y-5">
    <div class="grid gap-4 lg:grid-cols-2">
      <div class="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm">
        <div>
          <h3 class="text-sm font-semibold tracking-[0.18em] text-slate-500">JCC</h3>
          <div class="mt-3 text-4xl font-semibold text-slate-900">{{ stats.jcc.count }}</div>
          <div class="mt-1 text-xs text-slate-500">{{ t('jccjcg.countIncludesDeleted') }}</div>
        </div>
        <div v-if="jccAwardLevels.length > 0" class="mt-4 flex flex-wrap gap-2">
          <div
            v-for="level in jccAwardLevels"
            :key="`jcc-${level}`"
            class="flex h-18 w-18 shrink-0 flex-col items-center justify-center rounded-2xl border border-amber-300 bg-amber-50 text-amber-900"
          >
            <div class="text-[11px] font-semibold tracking-[0.18em]">JCC</div>
            <div class="mt-1 text-xl font-bold leading-none">{{ level }}</div>
          </div>
        </div>
        <div v-else class="mt-4 text-sm text-slate-700">{{ t('jccjcg.noneYet') }}</div>
        <div class="mt-2 text-xs text-slate-500">{{ t('jccjcg.jccLevels') }}</div>
      </div>

      <div class="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm">
        <div>
          <h3 class="text-sm font-semibold tracking-[0.18em] text-slate-500">JCG</h3>
          <div class="mt-3 text-4xl font-semibold text-slate-900">{{ stats.jcg.count }}</div>
          <div class="mt-1 text-xs text-slate-500">{{ t('jccjcg.countIncludesDeleted') }}</div>
        </div>
        <div v-if="jcgAwardLevels.length > 0" class="mt-4 flex flex-wrap gap-2">
          <div
            v-for="level in jcgAwardLevels"
            :key="`jcg-${level}`"
            class="flex h-18 w-18 shrink-0 flex-col items-center justify-center rounded-2xl border border-sky-300 bg-sky-50 text-sky-900"
          >
            <div class="text-[11px] font-semibold tracking-[0.18em]">JCG</div>
            <div class="mt-1 text-xl font-bold leading-none">{{ level }}</div>
          </div>
        </div>
        <div v-else class="mt-4 text-sm text-slate-700">{{ t('jccjcg.noneYet') }}</div>
        <div class="mt-2 text-xs text-slate-500">{{ t('jccjcg.jcgLevels') }}</div>
      </div>
    </div>

    <div class="grid gap-4 lg:grid-cols-2">
      <div class="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm">
        <div class="flex items-end justify-between gap-3">
          <div>
            <h3 class="text-sm font-semibold tracking-[0.18em] text-slate-500">WACA</h3>
            <div class="mt-3 text-2xl font-semibold text-slate-900">{{ wacaWorked }} / {{ wacaTotal }}</div>
          </div>
          <div class="text-sm font-medium text-slate-600">{{ formatPercent(wacaWorked, wacaTotal) }}</div>
        </div>
        <div class="mt-4 h-3 overflow-hidden rounded-full bg-slate-200">
          <div
            class="h-full rounded-full bg-emerald-500 transition-all"
            :style="{ width: wacaWidth }"
          />
        </div>
        <div class="mt-2 text-xs text-slate-500">{{ t('jccjcg.progressExcludesDeleted') }}</div>
      </div>

      <div class="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm">
        <div class="flex items-end justify-between gap-3">
          <div>
            <h3 class="text-sm font-semibold tracking-[0.18em] text-slate-500">WAGA</h3>
            <div class="mt-3 text-2xl font-semibold text-slate-900">{{ wagaWorked }} / {{ wagaTotal }}</div>
          </div>
          <div class="text-sm font-medium text-slate-600">{{ formatPercent(wagaWorked, wagaTotal) }}</div>
        </div>
        <div class="mt-4 h-3 overflow-hidden rounded-full bg-slate-200">
          <div
            class="h-full rounded-full bg-emerald-500 transition-all"
            :style="{ width: wagaWidth }"
          />
        </div>
        <div class="mt-2 text-xs text-slate-500">{{ t('jccjcg.progressExcludesDeleted') }}</div>
      </div>
    </div>

    <div class="rounded-2xl border border-slate-200 bg-white/90 p-4 shadow-sm">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div class="inline-flex w-fit rounded-full bg-slate-100 p-1">
          <button
            class="rounded-full px-4 py-2 text-sm font-medium transition-colors"
            :class="activeTab === 'jcc' ? 'bg-slate-900 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'"
            @click="activeTab = 'jcc'"
          >
            JCC
          </button>
          <button
            class="rounded-full px-4 py-2 text-sm font-medium transition-colors"
            :class="activeTab === 'jcg' ? 'bg-slate-900 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'"
            @click="activeTab = 'jcg'"
          >
            JCG
          </button>
        </div>

        <label class="flex items-center gap-2 text-sm text-slate-600 cursor-pointer">
          <input v-model="showDeleted" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-sky-600 focus:ring-sky-500" />
          {{ t('jccjcg.showDeleted') }}
        </label>
      </div>

      <div class="mt-4 flex flex-wrap gap-3 text-xs text-slate-600">
        <span class="font-semibold text-slate-700">{{ t('jccjcg.legend') }}</span>
        <span v-for="item in legendItems" :key="item.key" class="inline-flex items-center gap-2">
          <span class="inline-flex h-4 w-4 rounded border" :class="item.classes" />
          {{ item.label }}
        </span>
      </div>
    </div>

    <div class="space-y-3">
      <template v-if="activeTab === 'jcc'">
        <PrefectureBlock
          v-for="prefNo in activePrefectures"
          :key="'jcc-' + prefNo"
          :pref-no="prefNo"
          :entities="jccEntityGroups[prefNo]"
          :show-deleted="showDeleted"
        />
      </template>
      <template v-else>
        <PrefectureBlock
          v-for="prefNo in activePrefectures"
          :key="'jcg-' + prefNo"
          :pref-no="prefNo"
          :entities="jcgEntityGroups[prefNo]"
          :show-deleted="showDeleted"
        />
      </template>
    </div>
  </div>
</template>
