<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { formatDateYmd } from '../awards/jarl'
import type { AwardResults, QsoSlot } from '../types'

const props = defineProps<{
  stats: AwardResults
}>()

const { t, locale } = useI18n()

const BAND_KEYS = ['160m', '80m', '40m', '30m', '20m', '17m', '15m', '12m', '10m']
const MODE_KEYS = ['CW', 'PHONE', 'DATA']

const PROVINCES = [
  { code: 'BJ', zh: '北京', en: 'Beijing', ja: '北京' },
  { code: 'HL', zh: '黑龙江', en: 'Heilongjiang', ja: '黒竜江' },
  { code: 'JL', zh: '吉林', en: 'Jilin', ja: '吉林' },
  { code: 'LN', zh: '辽宁', en: 'Liaoning', ja: '遼寧' },
  { code: 'TJ', zh: '天津', en: 'Tianjin', ja: '天津' },
  { code: 'NM', zh: '内蒙古', en: 'Inner Mongolia', ja: '内蒙古' },
  { code: 'HE', zh: '河北', en: 'Hebei', ja: '河北' },
  { code: 'SX', zh: '山西', en: 'Shanxi', ja: '山西' },
  { code: 'SH', zh: '上海', en: 'Shanghai', ja: '上海' },
  { code: 'SD', zh: '山东', en: 'Shandong', ja: '山東' },
  { code: 'JS', zh: '江苏', en: 'Jiangsu', ja: '江蘇' },
  { code: 'ZJ', zh: '浙江', en: 'Zhejiang', ja: '浙江' },
  { code: 'JX', zh: '江西', en: 'Jiangxi', ja: '江西' },
  { code: 'FJ', zh: '福建', en: 'Fujian', ja: '福建' },
  { code: 'AH', zh: '安徽', en: 'Anhui', ja: '安徽' },
  { code: 'HA', zh: '河南', en: 'Henan', ja: '河南' },
  { code: 'HB', zh: '湖北', en: 'Hubei', ja: '湖北' },
  { code: 'HN', zh: '湖南', en: 'Hunan', ja: '湖南' },
  { code: 'GD', zh: '广东', en: 'Guangdong', ja: '広東' },
  { code: 'GX', zh: '广西', en: 'Guangxi', ja: '広西' },
  { code: 'HI', zh: '海南', en: 'Hainan', ja: '海南' },
  { code: 'SC', zh: '四川', en: 'Sichuan', ja: '四川' },
  { code: 'CQ', zh: '重庆', en: 'Chongqing', ja: '重慶' },
  { code: 'GZ', zh: '贵州', en: 'Guizhou', ja: '貴州' },
  { code: 'YN', zh: '云南', en: 'Yunnan', ja: '雲南' },
  { code: 'SN', zh: '陕西', en: 'Shaanxi', ja: '陝西' },
  { code: 'GS', zh: '甘肃', en: 'Gansu', ja: '甘粛' },
  { code: 'NX', zh: '宁夏', en: 'Ningxia', ja: '寧夏' },
  { code: 'QH', zh: '青海', en: 'Qinghai', ja: '青海' },
  { code: 'XJ', zh: '新疆', en: 'Xinjiang', ja: '新疆' },
  { code: 'XZ', zh: '西藏', en: 'Tibet', ja: 'チベット' },
  { code: 'TW', zh: '台湾', en: 'Taiwan', ja: '台湾' },
  { code: 'HK', zh: '香港', en: 'Hong Kong', ja: '香港' },
  { code: 'MO', zh: '澳门', en: 'Macau', ja: '澳門' },
] as const

function formatPercent(worked: number, total: number): string {
  if (total === 0) return '0%'
  return `${Math.round((worked / total) * 100)}%`
}

function provinceName(province: (typeof PROVINCES)[number]): string {
  if (locale.value === 'en') return province.en
  if (locale.value === 'ja') return province.ja
  return province.zh
}

function slotTitle(slot: QsoSlot | null): string {
  if (!slot) return t('wapc.notWorked')
  return `${slot.CALL}\n${formatDateYmd(slot.QSO_DATE)}\n${slot.BAND} ${slot.MODE}`
}

const bandCounts = computed(() => BAND_KEYS.map((band) => ({
  key: band,
  count: props.stats.wapc.bandCounts[band] || 0,
})))

const modeCounts = computed(() => MODE_KEYS.map((mode) => ({
  key: mode,
  count: props.stats.wapc.modeCounts[mode] || 0,
})))

const provinceRows = computed(() => PROVINCES.map((province) => ({
  ...province,
  mixed: props.stats.wapc.mixed[province.code] || null,
  bands: props.stats.wapc.band[province.code] || {},
  modes: props.stats.wapc.mode[province.code] || {},
})))
</script>

<template>
  <div class="space-y-5">
    <div class="grid gap-4 lg:grid-cols-3">
      <section class="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm">
        <h3 class="text-sm font-semibold tracking-[0.18em] text-slate-500">{{ t('wapc.mixed') }}</h3>
        <div class="mt-3 text-3xl font-semibold text-slate-900">{{ stats.wapc.mixedCount }} / 34</div>
        <div class="mt-1 text-sm text-slate-500">{{ formatPercent(stats.wapc.mixedCount, 34) }}</div>
      </section>

      <section class="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm">
        <h3 class="text-sm font-semibold tracking-[0.18em] text-slate-500">{{ t('wapc.bands') }}</h3>
        <div class="mt-4 flex flex-wrap gap-2">
          <span
            v-for="band in bandCounts"
            :key="band.key"
            class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700"
          >
            {{ band.key }} {{ band.count }}
          </span>
        </div>
      </section>

      <section class="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm">
        <h3 class="text-sm font-semibold tracking-[0.18em] text-slate-500">{{ t('wapc.modes') }}</h3>
        <div class="mt-4 flex flex-wrap gap-2">
          <span
            v-for="mode in modeCounts"
            :key="mode.key"
            class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700"
          >
            {{ mode.key }} {{ mode.count }}
          </span>
        </div>
      </section>
    </div>

    <section class="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm">
      <h3 class="text-sm font-semibold tracking-[0.18em] text-slate-500">{{ t('wapc.provinceGrid') }}</h3>
      <div class="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5">
        <div
          v-for="province in provinceRows"
          :key="province.code"
          class="rounded-2xl border p-3"
          :class="province.mixed ? 'border-emerald-200 bg-emerald-50 text-emerald-900' : 'border-slate-200 bg-slate-50 text-slate-600'"
          :title="slotTitle(province.mixed)"
        >
          <div class="flex items-center justify-between gap-2">
            <span class="text-xs font-mono text-slate-500">{{ province.code }}</span>
            <span class="text-xs font-medium">{{ province.mixed ? t('stats.worked') : t('wapc.notWorked') }}</span>
          </div>
          <div class="mt-2 text-sm font-semibold">{{ provinceName(province) }}</div>
          <template v-if="province.mixed">
            <div class="mt-2 text-xs">{{ province.mixed.CALL }}</div>
            <div class="text-xs">{{ formatDateYmd(province.mixed.QSO_DATE) }}</div>
            <div class="text-xs">{{ province.mixed.BAND }} {{ province.mixed.MODE }}</div>
          </template>
        </div>
      </div>
    </section>

    <section class="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm">
      <h3 class="text-sm font-semibold tracking-[0.18em] text-slate-500">{{ t('wapc.bandMatrix') }}</h3>
      <div class="mt-4 overflow-x-auto rounded-2xl border border-slate-200">
        <table class="min-w-full border-collapse text-sm">
          <thead>
            <tr class="border-b border-slate-200 bg-slate-50 text-slate-600">
              <th class="px-4 py-3 text-left font-medium">{{ t('wapc.provinces') }}</th>
              <th
                v-for="band in BAND_KEYS"
                :key="band"
                class="px-4 py-3 text-center font-medium whitespace-nowrap"
              >
                {{ band }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="province in provinceRows" :key="`band-${province.code}`" class="border-t border-slate-100">
              <td class="px-4 py-3 text-slate-800 whitespace-nowrap">
                <span class="font-mono text-xs text-slate-500">{{ province.code }}</span>
                <span class="ml-2 font-medium">{{ provinceName(province) }}</span>
              </td>
              <td v-for="band in BAND_KEYS" :key="`${province.code}-${band}`" class="px-4 py-3 text-center">
                <div
                  class="mx-auto h-5 w-5 rounded-md border"
                  :class="province.bands[band] ? 'border-emerald-600 bg-emerald-500' : 'border-slate-300 bg-white'"
                  :title="slotTitle(province.bands[band] || null)"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm">
      <h3 class="text-sm font-semibold tracking-[0.18em] text-slate-500">{{ t('wapc.modeMatrix') }}</h3>
      <div class="mt-4 overflow-x-auto rounded-2xl border border-slate-200">
        <table class="min-w-full border-collapse text-sm">
          <thead>
            <tr class="border-b border-slate-200 bg-slate-50 text-slate-600">
              <th class="px-4 py-3 text-left font-medium">{{ t('wapc.provinces') }}</th>
              <th
                v-for="mode in MODE_KEYS"
                :key="mode"
                class="px-4 py-3 text-center font-medium whitespace-nowrap"
              >
                {{ mode }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="province in provinceRows" :key="`mode-${province.code}`" class="border-t border-slate-100">
              <td class="px-4 py-3 text-slate-800 whitespace-nowrap">
                <span class="font-mono text-xs text-slate-500">{{ province.code }}</span>
                <span class="ml-2 font-medium">{{ provinceName(province) }}</span>
              </td>
              <td v-for="mode in MODE_KEYS" :key="`${province.code}-${mode}`" class="px-4 py-3 text-center">
                <div
                  class="mx-auto h-5 w-5 rounded-md border"
                  :class="province.modes[mode] ? 'border-sky-600 bg-sky-500' : 'border-slate-300 bg-white'"
                  :title="slotTitle(province.modes[mode] || null)"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>