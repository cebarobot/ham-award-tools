import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { AwardResults } from '../types'

export const useAwardStore = defineStore('award', () => {
  const results = ref<AwardResults | null>(null)
  const loaded = computed(() => results.value !== null)

  function setResults(r: AwardResults) {
    results.value = r
  }

  function clear() {
    results.value = null
  }

  return { results, loaded, setResults, clear }
})
