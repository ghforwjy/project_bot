import api from './api'

export interface LLMConfig {
  provider: string
  api_key: string
  base_url: string
  model: string
  temperature: number
  max_tokens: number
}

export interface ConfigUpdate {
  llm?: LLMConfig
  language?: string
  theme?: string
}

export interface ValidateConfig {
  provider: string
  api_key: string
  base_url?: string
}

export const configService = {
  // 获取配置
  getConfig: async () => {
    const response = await api.get('/config')
    return response.data
  },

  // 更新配置
  updateConfig: async (data: ConfigUpdate) => {
    const response = await api.put('/config', data)
    return response.data
  },

  // 验证配置
  validateConfig: async (data: ValidateConfig) => {
    const response = await api.post('/config/validate', data)
    return response.data
  }
}
