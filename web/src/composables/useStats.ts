import { ref } from 'vue'
import type { Qso, AwardResults } from '../types'
import { useCache } from './useCache'
import { computeAllAwards } from '../awards'

const qsos = ref<Qso[]>([])
const stats = ref<AwardResults | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const fileName = ref('')

export function useStats() {
  const cache = useCache()

  async function init(): Promise<void> {
    try {
      const cached = await cache.loadAll()
      qsos.value = cached
      if (cached.length > 0) {
        stats.value = computeAllAwards(cached)
      }
    } catch (e) {
      error.value = `Failed to load cache: ${e}`
    }
  }

  async function processFile(file: File): Promise<void> {
    loading.value = true
    error.value = null
    fileName.value = file.name

    try {
      const { parseAdifFile } = await import('./useAdifParser')
      const newQsos = await parseAdifFile(file)

      if (newQsos.length === 0) {
        error.value = 'No QSO records found in file'
        loading.value = false
        return
      }

      const merged = cache.mergeQsos(qsos.value, newQsos)
      qsos.value = merged
      stats.value = computeAllAwards(merged)
      await cache.saveAll(merged)
    } catch (e) {
      error.value = `Failed to process file: ${e}`
    } finally {
      loading.value = false
    }
  }

  async function clearAll(): Promise<void> {
    await cache.clearAll()
    qsos.value = []
    stats.value = null
    fileName.value = ''
    error.value = null
  }

  return { qsos, stats, loading, error, fileName, init, processFile, clearAll }
}
