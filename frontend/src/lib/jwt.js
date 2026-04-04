export function getUsernameFromToken(token) {
  if (!token) return ''
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return typeof payload.sub === 'string' ? payload.sub : ''
  } catch {
    return ''
  }
}
