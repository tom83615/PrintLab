export async function requestJson(url, options) {
  const response = await fetch(url, {cache: 'no-store', ...options});
  let data = {};
  try { data = await response.json(); } catch {}
  if (!response.ok) {
    throw new Error(data.detail || data.message || data.error || `請求失敗 (${response.status})`);
  }
  return data;
}
