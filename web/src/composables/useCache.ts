import { openDB } from 'idb'
import type { Qso } from '../types'

const DB_NAME = 'ham-award-tools'
const DB_VERSION = 1
const STORE_NAME = 'qsos'

async function getDb() {
  return openDB(DB_NAME, DB_VERSION, {
    upgrade(db) {
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'id', autoIncrement: true })
      }
    },
  })
}

let cachedCount = -1
let cachedQsos: Qso[] | null = null

export function useCache() {
  async function loadAll(): Promise<Qso[]> {
    if (cachedQsos) return cachedQsos
    const db = await getDb()
    cachedQsos = await db.getAll(STORE_NAME)
    cachedCount = cachedQsos.length
    return cachedQsos
  }

  async function saveAll(qsos: Qso[]): Promise<void> {
    const db = await getDb()
    const tx = db.transaction(STORE_NAME, 'readwrite')
    const store = tx.objectStore(STORE_NAME)
    await store.clear()
    for (const qso of qsos) {
      await store.add(qso)
    }
    await tx.done
    cachedQsos = [...qsos]
    cachedCount = qsos.length
  }

  function mergeQsos(existing: Qso[], incoming: Qso[]): Qso[] {
    const merged = new Map<string, Qso>()

    for (const qso of existing) {
      const key = qsoKey(qso)
      const prev = merged.get(key)
      if (!prev || qso.QSO_DATE < prev.QSO_DATE) {
        merged.set(key, qso)
      }
    }

    for (const qso of incoming) {
      const key = qsoKey(qso)
      const prev = merged.get(key)
      if (!prev || qso.QSO_DATE < prev.QSO_DATE) {
        merged.set(key, qso)
      }
    }

    return Array.from(merged.values())
  }

  function qsoKey(qso: Qso): string {
    const call = qso.CALL || ''
    const band = qso.BAND || ''
    const mode = qso.MODE || ''
    const date = qso.QSO_DATE || ''
    const cnty = qso.CNTY || ''
    const state = qso.STATE || ''
    return `${call}|${band}|${mode}|${date}|${cnty}|${state}`
  }

  async function clearAll(): Promise<void> {
    const db = await getDb()
    const tx = db.transaction(STORE_NAME, 'readwrite')
    await tx.objectStore(STORE_NAME).clear()
    await tx.done
    cachedQsos = null
    cachedCount = 0
  }

  return { loadAll, saveAll, mergeQsos, clearAll }
}
