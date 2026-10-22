// Drift detection only, never authorization. Store no protected lesson prose in
// public bundles. Content still comes exclusively from the authorized lesson API.
export function sourceFingerprint(value) {
  let hash = 14695981039346656037n
  for (const character of value) {
    hash = BigInt.asUintN(64, (hash ^ BigInt(character.codePointAt(0))) * 1099511628211n)
  }
  return `${Array.from(value).length}:${hash.toString(16).padStart(16, '0')}`
}
