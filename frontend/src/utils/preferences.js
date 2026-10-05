// Preferences should still work for this visit if browser storage is unavailable.
export function readPreference(key) {
  try {
    return localStorage.getItem(key)
  } catch {
    return null
  }
}

export function savePreference(key, value) {
  try {
    localStorage.setItem(key, value)
  } catch {
    // Private or restricted browsers may block persistent storage.
  }
}
