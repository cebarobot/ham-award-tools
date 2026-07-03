<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useStats } from './composables/useStats'
import { useCsvExport } from './composables/useCsvExport'
import { onMounted, ref } from 'vue'

const { t, locale } = useI18n()
const { stats, loading, error, fileName, init, processFile, clearAll } = useStats()
const { downloadCsv, generateAjdCsv, generateWajaCsv, generateJccCsv, generateJcgCsv, generateAjaCsv, generateAjaListCsv, generateAjaTotalTableCsv, generateWapcBandCsv, generateWapcModeCsv } = useCsvExport()

const dropZone = ref<HTMLElement | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const isOver = ref(false)

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

const csvEntries: Array<{ name: string; key: string; generate: () => string }> = [
  { name: 'AJD', key: 'ajd', generate: () => generateAjdCsv(stats.value!) },
  { name: 'WAJA', key: 'waja', generate: () => generateWajaCsv(stats.value!) },
  { name: 'JCC', key: 'jcc', generate: () => generateJccCsv(stats.value!) },
  { name: 'JCG', key: 'jcg', generate: () => generateJcgCsv(stats.value!) },
  { name: 'AJA', key: 'aja', generate: () => generateAjaCsv(stats.value!) },
  { name: 'AJA (List)', key: 'ajaList', generate: () => generateAjaListCsv(stats.value!) },
  { name: 'AJA (Total)', key: 'ajaTotal', generate: () => generateAjaTotalTableCsv(stats.value!) },
  { name: 'WAPC (Band)', key: 'wapcBand', generate: () => generateWapcBandCsv(stats.value!) },
  { name: 'WAPC (Mode)', key: 'wapcMode', generate: () => generateWapcModeCsv(stats.value!) },
]
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
          Clear
        </button>
      </div>
    </header>

    <main class="flex-1 max-w-3xl mx-auto w-full p-4 space-y-6">
      <div
        ref="dropZone"
        class="border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors"
        :class="[
          isOver
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-950'
            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400',
          loading ? 'opacity-50' : '',
        ]"
        @click="triggerFileInput"
      >
        <p v-if="loading" class="text-gray-500">Processing...</p>
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
        <section class="border rounded-lg p-4">
          <h2 class="text-sm font-medium text-gray-500 mb-3">Statistics</h2>
          <div class="grid grid-cols-3 sm:grid-cols-4 gap-3 text-center">
            <div class="p-2 bg-gray-50 dark:bg-gray-800 rounded">
              <div class="text-lg font-bold">{{ stats.ajdCount }}/10</div>
              <div class="text-xs text-gray-500">AJD</div>
            </div>
            <div class="p-2 bg-gray-50 dark:bg-gray-800 rounded">
              <div class="text-lg font-bold">{{ stats.wajaCount }}/47</div>
              <div class="text-xs text-gray-500">WAJA</div>
            </div>
            <div class="p-2 bg-gray-50 dark:bg-gray-800 rounded">
              <div class="text-lg font-bold">{{ stats.jcc.count }}</div>
              <div class="text-xs text-gray-500">JCC</div>
            </div>
            <div class="p-2 bg-gray-50 dark:bg-gray-800 rounded">
              <div class="text-lg font-bold">{{ stats.jcg.count }}</div>
              <div class="text-xs text-gray-500">JCG</div>
            </div>
            <div class="p-2 bg-gray-50 dark:bg-gray-800 rounded">
              <div class="text-lg font-bold">{{ stats.aja.count }}</div>
              <div class="text-xs text-gray-500">AJA</div>
            </div>
            <div class="p-2 bg-gray-50 dark:bg-gray-800 rounded">
              <div class="text-lg font-bold">{{ stats.wapc.mixedCount }}/34</div>
              <div class="text-xs text-gray-500">WAPC</div>
            </div>
            <div class="p-2 bg-gray-50 dark:bg-gray-800 rounded">
              <div class="text-lg font-bold">{{ stats.waca.count }}</div>
              <div class="text-xs text-gray-500">WACA</div>
            </div>
            <div class="p-2 bg-gray-50 dark:bg-gray-800 rounded">
              <div class="text-lg font-bold">{{ stats.waga.count }}</div>
              <div class="text-xs text-gray-500">WAGA</div>
            </div>
          </div>
        </section>

        <section class="border rounded-lg p-4">
          <h2 class="text-sm font-medium text-gray-500 mb-3">CSV Download</h2>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="csv in csvEntries"
              :key="csv.key"
              class="text-sm px-3 py-1.5 rounded border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              @click="downloadCsv(`checksheet_${csv.key}.csv`, csv.generate())"
            >
              {{ csv.name }}
            </button>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>
