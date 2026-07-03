<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()

const tabs = [
  { key: 'jccjcg', labelKey: 'awards.jcc', extra: '/JCG/WACA/WAGA' },
  { key: 'aja', labelKey: 'awards.aja', extra: '' },
  { key: 'ajdwaja', labelKey: 'awards.ajd', extra: '/WAJA' },
  { key: 'wapc', labelKey: 'awards.wapc', extra: '' },
]
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <header class="border-b border-gray-200 dark:border-gray-800 px-4 py-3 flex items-center justify-between">
      <h1 class="text-lg font-semibold">{{ t('title') }}</h1>
      <select
        v-model="locale"
        class="text-sm border rounded px-2 py-1 bg-transparent"
      >
        <option value="zh">中文</option>
        <option value="en">English</option>
        <option value="ja">日本語</option>
      </select>
    </header>

    <div class="flex-1 max-w-6xl mx-auto w-full p-4">
      <div class="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-12 text-center text-gray-500">
        {{ t('dropHint') }}
      </div>
    </div>
  </div>
</template>
