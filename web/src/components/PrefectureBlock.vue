<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { EntityInfo, QsoSlot } from '../types'
import { PREF_LIST } from '../awards/jarl'
import EntityPill from './EntityPill.vue'

const props = defineProps<{
  prefNo: string
  entities: Array<{ no: string; entity: EntityInfo; qso: QsoSlot | null }>
  showDeleted: boolean
}>()

const { t, locale } = useI18n()

const prefName = computed(() => {
  const pref = PREF_LIST[props.prefNo]
  if (!pref) return props.prefNo
  return locale.value === 'en' ? pref.romaji : pref.kanji
})
const visibleEntities = computed(() => props.entities.filter((e) => !e.entity.deleted || props.showDeleted))
const workedCount = computed(() => visibleEntities.value.filter((entity) => entity.qso !== null).length)
const totalCount = computed(() => visibleEntities.value.length)
</script>

<template>
  <div v-if="visibleEntities.length > 0" class="rounded-2xl border border-slate-200 bg-white/80 p-3 shadow-sm backdrop-blur-sm sm:p-4">
    <div class="mb-3 flex flex-wrap items-center justify-between gap-2">
      <div class="flex items-center gap-2">
        <span class="inline-flex rounded-full bg-slate-900 px-2.5 py-1 text-[11px] font-semibold tracking-wide text-white">{{ prefNo }}</span>
        <h4 class="text-sm font-semibold text-slate-800">{{ prefName }}</h4>
      </div>
      <div class="text-xs text-slate-500">
        {{ t('stats.worked') }} {{ workedCount }} / {{ totalCount }}
      </div>
    </div>
    <div class="flex flex-wrap gap-1.5">
      <EntityPill
        v-for="item in visibleEntities"
        :key="item.no"
        :no="item.no"
        :entity="item.entity"
        :qso="item.qso"
        :show-deleted="showDeleted"
      />
    </div>
  </div>
</template>
