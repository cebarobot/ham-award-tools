<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { EntityInfo, QsoSlot } from '../types'

const props = defineProps<{
  no: string
  entity: EntityInfo
  qso: QsoSlot | null
  showDeleted: boolean
}>()

const { t, locale } = useI18n()

const label = computed(() => props.no.substring(2))
const worked = computed(() => props.qso !== null)
const isDeleted = computed(() => props.entity.deleted === true)
const shouldShow = computed(() => !isDeleted.value || props.showDeleted)
const entityName = computed(() => locale.value === 'en' ? props.entity.name : props.entity.ja_name)
const tooltipId = computed(() => `entity-tooltip-${props.no}`)

const showTooltip = ref(false)

function fmtDate(dateStr?: string): string {
  if (!dateStr || dateStr.length !== 8) return dateStr || ''
  return dateStr.substring(0, 4) + '-' + dateStr.substring(4, 6) + '-' + dateStr.substring(6, 8)
}
</script>

<template>
  <div
    v-if="shouldShow"
    class="relative"
    @mouseenter="showTooltip = true"
    @mouseleave="showTooltip = false"
  >
    <button
      type="button"
      class="inline-flex h-10 w-10 items-center justify-center rounded-lg border text-[11px] font-semibold font-mono transition-colors duration-150 cursor-default select-none focus-visible:border-sky-500 focus-visible:outline-none"
      :class="[
        worked
          ? isDeleted
            ? 'border-emerald-400 bg-emerald-200/80 text-emerald-950 striped'
            : 'border-emerald-600 bg-emerald-500 text-white'
          : isDeleted
            ? 'border-slate-300 bg-slate-100 text-slate-400 striped'
            : 'border-slate-300 bg-white text-slate-500',
      ]"
      :aria-describedby="showTooltip ? tooltipId : undefined"
      :aria-label="`${props.no} ${entityName}`"
      @focus="showTooltip = true"
      @blur="showTooltip = false"
    >
      {{ label }}
    </button>
    <div
      v-if="showTooltip"
      :id="tooltipId"
      class="pointer-events-none absolute bottom-full left-1/2 z-50 mb-2 min-w-32 max-w-56 -translate-x-1/2 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-white"
    >
      <div class="space-y-1 text-left">
        <div class="font-semibold text-white">{{ no }} {{ entityName }}</div>
        <div v-if="entity.deleted" class="text-amber-300">
          {{ t('jccjcg.deleted') }}<span v-if="entity.deleted_date"> {{ fmtDate(entity.deleted_date) }}</span>
        </div>
        <template v-if="qso">
          <div>{{ qso.CALL }}</div>
          <div>{{ fmtDate(qso.QSO_DATE) }}</div>
          <div>{{ qso.BAND }} {{ qso.MODE }}</div>
        </template>
        <div v-else class="text-slate-300">{{ t('jccjcg.notWorked') }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.striped {
  background-image: repeating-linear-gradient(
    -45deg,
    transparent,
    transparent 2px,
    rgba(0, 0, 0, 0.08) 2px,
    rgba(0, 0, 0, 0.08) 4px
  );
}
</style>
