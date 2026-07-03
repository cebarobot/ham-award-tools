import { defineStore } from 'pinia'
import { reactive, computed } from 'vue'
import type { AwardResults } from '../types'

export const useAwardStore = defineStore('award', () => {
  const results = reactive<AwardResults | null>(null)
  const loaded = computed(() => results !== null)

  function setResults(r: AwardResults) {
    Object.assign(results, r)
  }

  function clear() {
    results = null
  }

  return { results, loaded, setResults, clear }
})
