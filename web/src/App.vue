<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useStats } from './composables/useStats'
import { useCsvExport } from './composables/useCsvExport'
import { computed, onMounted, ref } from 'vue'
import JccJcgView from './components/JccJcgView.vue'

const { t, locale } = useI18n()
const { stats, loading, error, fileName, init, processFile, clearAll } = useStats()
const { downloadCsv, generateAjdCsv, generateWajaCsv, generateJccCsv, generateJcgCsv, generateAjaCsv, generateAjaListCsv, generateAjaTotalTableCsv, generateWapcBandCsv, generateWapcModeCsv } = useCsvExport()

const fileInput = ref<HTMLInputElement | null>(null)
const isOver = ref(false)
const activeTab = ref<'summary' | 'jccjcg' | 'aja' | 'ajdwaja' | 'wapc'>('summary')

function triggerFileInput() {
  fileInput.value?.click()
}

onMounted(() => {
  init()
})

function handleDrop(e: DragEvent) {
  e.preventDefault()
  isOver.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) processFile(file)
}

function handleFileInput(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) processFile(file)
}

const csvEntries: Array<{ labelKey: keyof typeof import('./locales/zh.json')['csv']; key: string; generate: () => string }> = [
  { labelKey: 'ajd', key: 'ajd', generate: () => generateAjdCsv(stats.value!) },
  { labelKey: 'waja', key: 'waja', generate: () => generateWajaCsv(stats.value!) },
  { labelKey: 'jcc', key: 'jcc', generate: () => generateJccCsv(stats.value!) },
  { labelKey: 'jcg', key: 'jcg', generate: () => generateJcgCsv(stats.value!) },
  { labelKey: 'aja', key: 'aja', generate: () => generateAjaCsv(stats.value!) },
  { labelKey: 'ajaList', key: 'ajaList', generate: () => generateAjaListCsv(stats.value!) },
  { labelKey: 'ajaTotal', key: 'ajaTotal', generate: () => generateAjaTotalTableCsv(stats.value!) },
  { labelKey: 'wapcBand', key: 'wapcBand', generate: () => generateWapcBandCsv(stats.value!) },
  { labelKey: 'wapcMode', key: 'wapcMode', generate: () => generateWapcModeCsv(stats.value!) },
]

const tabs = computed(() => [
  { key: 'summary' as const, label: t('awards.summary') },
  { key: 'jccjcg' as const, label: `${t('awards.jcc')}/${t('awards.jcg')}` },
  { key: 'aja' as const, label: t('awards.aja') },
  { key: 'ajdwaja' as const, label: `${t('awards.ajd')}/${t('awards.waja')}` },
  { key: 'wapc' as const, label: t('awards.wapc') },
])
</script>

<template>
  <div class="min-h-screen flex flex-col" @dragover.prevent="isOver = true" @dragleave.prevent="isOver = false" @drop.prevent="handleDrop">
    <header class="border-b border-gray-200 dark:border-gray-800 px-4 py-3 flex items-center justify-between">
      <h1 class="text-lg font-semibold">{{ t('title') }}</h1>
      <div class="flex items-center gap-2">
        <select
          v-model="locale"
          class="text-sm border rounded px-2 py-1 bg-transparent"
        >
          <option value="zh">中文</option>
          <option value="en">English</option>
          <option value="ja">日本語</option>
        </select>
        <button
          v-if="stats"
          class="text-sm text-red-500 hover:text-red-700 px-2 py-1"
          @click="clearAll"
        >
          {{ t('common.clear') }}
        </button>
      </div>
    </header>

    <main class="flex-1 max-w-4xl mx-auto w-full p-4 space-y-6">
      <div
        class="border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors"
        :class="[
          isOver
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-950'
            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400',
          loading ? 'opacity-50' : '',
        ]"
        @click="triggerFileInput"
      >
        <p v-if="loading" class="text-gray-500">{{ t('common.processing') }}</p>
        <p v-else-if="fileName" class="text-gray-700 dark:text-gray-300">
          {{ fileName }}
          <br>
          <span class="text-sm text-gray-500">{{ t('dropHint') }}</span>
        </p>
        <p v-else class="text-gray-500">{{ t('dropHint') }}</p>
      </div>

      <input
        ref="fileInput"
        type="file"
        accept=".adi"
        class="hidden"
        @change="handleFileInput"
      />

      <div v-if="error" class="text-red-500 text-sm text-center">{{ error }}</div>

      <div v-if="stats" class="space-y-6">
        <nav class="flex border-b border-gray-200 dark:border-gray-700 gap-0">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="px-4 py-2 text-sm border-b-2 transition-colors"
            :class="activeTab === tab.key
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </nav>

        <template v-if="activeTab === 'summary'">
          <section class="border rounded-lg p-4">
            <h2 class="text-sm font-medium text-gray-500 mb-3">{{ t('common.statistics') }}</h2>
            <div class="grid grid-cols-3 sm:grid-cols-4 gap-3 text-center">
              <div class="p-2 bg-gray-50 dark:bg-gray-800 rounded">
                <div class="text-lg font-bold">{{ stats.ajdCount }}/10</div>
                <div class="text-xs text-gray-500">{{ t('awards.ajd') }}</div>
              </div>
              <div class="p-2 bg-gray-50 dark:bg-gray-800 rounded">
                <div class="text-lg font-bold">{{ stats.wajaCount }}/47</div>
                <div class="text-xs text-gray-500">{{ t('awards.waja') }}</div>
              </div>
              <div class="p-2 bg-gray-50 dark:bg-gray-800 rounded">
                <div class="text-lg font-bold">{{ stats.jcc.count }}</div>
                <div class="text-xs text-gray-500">{{ t('awards.jcc') }}</div>
              </div>
              <div class="p-2 bg-gray-50 dark:bg-gray-800 rounded">
                <div class="text-lg font-bold">{{ stats.jcg.count }}</div>
                <div class="text-xs text-gray-500">{{ t('awards.jcg') }}</div>
              </div>
              <div class="p-2 bg-gray-50 dark:bg-gray-800 rounded">
                <div class="text-lg font-bold">{{ stats.aja.count }}</div>
                <div class="text-xs text-gray-500">{{ t('awards.aja') }}</div>
              </div>
              <div class="p-2 bg-gray-50 dark:bg-gray-800 rounded">
                <div class="text-lg font-bold">{{ stats.wapc.mixedCount }}/34</div>
                <div class="text-xs text-gray-500">{{ t('awards.wapc') }}</div>
              </div>
              <div class="p-2 bg-gray-50 dark:bg-gray-800 rounded">
                <div class="text-lg font-bold">{{ stats.waca.count }}</div>
                <div class="text-xs text-gray-500">{{ t('awards.waca') }}</div>
              </div>
              <div class="p-2 bg-gray-50 dark:bg-gray-800 rounded">
                <div class="text-lg font-bold">{{ stats.waga.count }}</div>
                <div class="text-xs text-gray-500">{{ t('awards.waga') }}</div>
              </div>
            </div>
          </section>

          <section class="border rounded-lg p-4">
            <h2 class="text-sm font-medium text-gray-500 mb-3">{{ t('csv.download') }}</h2>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="csv in csvEntries"
                :key="csv.key"
                class="text-sm px-3 py-1.5 rounded border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                @click="downloadCsv(`checksheet_${csv.key}.csv`, csv.generate())"
              >
                {{ t(`csv.${csv.labelKey}`) }}
              </button>
            </div>
          </section>
        </template>

        <JccJcgView v-if="activeTab === 'jccjcg'" :stats="stats" />

        <div v-if="activeTab === 'aja'" class="border rounded-lg p-8 text-center text-gray-500">
          AJA view — coming in Phase 5
        </div>

        <div v-if="activeTab === 'ajdwaja'" class="border rounded-lg p-8 text-center text-gray-500">
          AJD/WAJA view — coming in Phase 6
        </div>

        <div v-if="activeTab === 'wapc'" class="border rounded-lg p-8 text-center text-gray-500">
          WAPC view — coming in Phase 6
        </div>
      </div>
    </main>
  </div>
</template>
