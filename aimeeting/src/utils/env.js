// Vite 环境变量处理
// Vite 使用 import.meta.env，但为了兼容 Vue 2 的写法，这里做一层转换
export const getEnv = (key, defaultValue = '') => {
  // 在 Vite 中，环境变量需要以 VITE_ 开头，但为了兼容，我们同时支持 VUE_APP_ 前缀
  const viteKey = key.replace('VUE_APP_', 'VITE_')
  return import.meta.env[viteKey] || import.meta.env[key] || defaultValue
}

// 导出常用的环境变量
export const API_BASE_URL = getEnv('VUE_APP_API_BASE_URL', '/api')
export const WEBSOCKET_BASE_URL = getEnv('VUE_APP_WEBSOCKET_BASE_URL', '/metwebsocket')

// 导出所有接口地址配置
export const API_UPLOAD_AUDIO = `${API_BASE_URL}/upload/audio`
export const API_UPLOAD = `${API_BASE_URL}/upload`
export const API_GET_TRANSCRIPT = `${API_BASE_URL}/get_transcript`
export const API_GENERATE_SUMMARY = `${API_BASE_URL}/generate_summary`
export const API_PROMPT_DEFAULT = `${API_BASE_URL}/prompt/default`
export const API_GENERATE_DOCX = `${API_BASE_URL}/generate_docx`

// WebSocket 完整URL（根据当前协议自动选择 ws:// 或 wss://）
export const getWebSocketUrl = () => {
  const wsBaseUrl = WEBSOCKET_BASE_URL
  // 如果配置的是完整URL（包含协议），直接使用
  if (wsBaseUrl.startsWith('ws://') || wsBaseUrl.startsWith('wss://')) {
    return wsBaseUrl
  }
  // 否则根据当前页面协议构建完整URL
  const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = location.host
  // 如果配置的路径以 / 开头，直接拼接
  if (wsBaseUrl.startsWith('/')) {
    return `${protocol}//${host}${wsBaseUrl}`
  }
  // 否则拼接 /
  return `${protocol}//${host}/${wsBaseUrl}`
}


