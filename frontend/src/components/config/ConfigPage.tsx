import React, { useState, useEffect } from 'react'
import { Card, Form, Input, Select, Button, Radio, Slider, message, Spin } from 'antd'
import { ArrowLeftOutlined, CheckCircleOutlined, SaveOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'

const { Option } = Select

interface LLMConfig {
  provider: string
  api_key: string
  base_url: string
  model: string
  temperature: number
  max_tokens: number
}

const PROVIDERS = [
  { value: 'openai', label: 'OpenAI', defaultUrl: 'https://api.openai.com/v1' },
  { value: 'kimi', label: 'Kimi (Moonshot)', defaultUrl: 'https://api.moonshot.cn/v1' },
  { value: 'doubao', label: '豆包 (字节跳动)', defaultUrl: 'https://ark.cn-beijing.volces.com/api/v3' }
]

const MODELS: Record<string, string[]> = {
  openai: ['gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo'],
  kimi: ['kimi-k2-turbo-preview', 'moonshot-v1-8k', 'moonshot-v1-32k', 'moonshot-v1-128k'],
  doubao: ['doubao-pro-32k', 'doubao-pro-4k', 'doubao-lite-32k']
}

const ConfigPage: React.FC = () => {
  const navigate = useNavigate()
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [testing, setTesting] = useState(false)
  const [provider, setProvider] = useState('openai')

  // 加载配置
  useEffect(() => {
    fetchConfig()
  }, [])

  const fetchConfig = async () => {
    try {
      const response = await fetch('/api/v1/config')
      const result = await response.json()
      
      if (result.code === 200 && result.data) {
        const llmConfig = result.data.llm || {}
        const chatConfig = result.data.chat || {}
        const projectConfig = result.data.project || {}
        const provider = llmConfig.provider || 'openai'
        setProvider(provider)
        
        form.setFieldsValue({
          provider,
          api_key: llmConfig.api_key || '',
          base_url: llmConfig.base_url || PROVIDERS.find(p => p.value === provider)?.defaultUrl,
          model: llmConfig.model || MODELS[provider][0],
          temperature: parseFloat(llmConfig.temperature) || 0.7,
          max_tokens: parseInt(llmConfig.max_tokens) || 2000,
          context_window: parseInt(chatConfig.context_window) || 10,
          auto_refresh: projectConfig.auto_refresh === 'true',
          refresh_interval: parseInt(projectConfig.refresh_interval) || 30000
        })
      }
    } catch (error) {
      message.error('加载配置失败')
    }
  }

  // 测试连接
  const handleTest = async () => {
    const values = form.getFieldsValue()
    
    if (!values.api_key) {
      message.warning('请输入API Key')
      return
    }

    setTesting(true)
    try {
      const response = await fetch('/api/v1/config/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: values.provider,
          api_key: values.api_key,
          base_url: values.base_url
        })
      })

      const result = await response.json()

      if (result.data?.valid) {
        message.success('连接成功！')
        if (result.data.available_models) {
          message.info(`可用模型: ${result.data.available_models.join(', ')}`)
        }
      } else {
        message.error(result.data?.message || '连接失败')
      }
    } catch (error) {
      message.error('测试连接失败')
    } finally {
      setTesting(false)
    }
  }

  // 保存配置
  const handleSave = async (values: any) => {
    setLoading(true)
    try {
      const response = await fetch('/api/v1/config', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          llm: {
            provider: values.provider,
            api_key: values.api_key,
            base_url: values.base_url,
            model: values.model,
            temperature: values.temperature.toString(),
            max_tokens: values.max_tokens.toString()
          },
          chat: {
            context_window: values.context_window.toString()
          },
          project: {
            auto_refresh: values.auto_refresh.toString(),
            refresh_interval: values.refresh_interval.toString()
          }
        })
      })

      const result = await response.json()

      if (result.code === 200) {
        message.success('配置已保存')
        navigate('/')
      } else {
        message.error(result.message || '保存失败')
      }
    } catch (error) {
      message.error('保存配置失败')
    } finally {
      setLoading(false)
    }
  }

  // 切换提供商
  const handleProviderChange = (value: string) => {
    setProvider(value)
    const providerConfig = PROVIDERS.find(p => p.value === value)
    
    form.setFieldsValue({
      base_url: providerConfig?.defaultUrl,
      model: MODELS[value][0]
    })
  }

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-2xl mx-auto">
        <Card
          title={
            <div className="flex items-center gap-4">
              <Button 
                icon={<ArrowLeftOutlined />} 
                onClick={() => navigate('/')}
              >
                返回
              </Button>
              <span>系统配置</span>
            </div>
          }
        >
          <Form
            form={form}
            layout="vertical"
            onFinish={handleSave}
            initialValues={{
              provider: 'openai',
              temperature: 0.7,
              max_tokens: 2000,
              context_window: 10,
              auto_refresh: true,
              refresh_interval: 30000
            }}
          >
            {/* LLM提供商选择 */}
            <Form.Item
              label="LLM提供商"
              name="provider"
              rules={[{ required: true }]}
            >
              <Radio.Group onChange={(e) => handleProviderChange(e.target.value)}>
                {PROVIDERS.map(p => (
                  <Radio.Button key={p.value} value={p.value}>
                    {p.label}
                  </Radio.Button>
                ))}
              </Radio.Group>
            </Form.Item>

            {/* API配置 */}
            <Form.Item
              label="Base URL"
              name="base_url"
              rules={[{ required: true }]}
            >
              <Input placeholder="https://api.openai.com/v1" />
            </Form.Item>

            <Form.Item
              label="API Key"
              name="api_key"
              rules={[{ required: true, message: '请输入API Key' }]}
            >
              <Input.Password placeholder="sk-..." />
            </Form.Item>

            <Form.Item
              label="Model"
              name="model"
              rules={[{ required: true }]}
            >
              <Select>
                {MODELS[provider]?.map(model => (
                  <Option key={model} value={model}>{model}</Option>
                ))}
              </Select>
            </Form.Item>

            {/* 高级设置 */}
            <Form.Item
              label={`Temperature: ${form.getFieldValue('temperature') || 0.7}`}
              name="temperature"
            >
              <Slider
                min={0}
                max={2}
                step={0.1}
                marks={{ 0: '0', 1: '1', 2: '2' }}
              />
            </Form.Item>

            <Form.Item
              label="Max Tokens"
              name="max_tokens"
            >
              <Input type="number" min={100} max={8000} />
            </Form.Item>

            {/* 聊天配置 */}
            <Card title="聊天配置" className="mt-6">
              <Form.Item
                label="上下文窗口大小"
                name="context_window"
                tooltip="保留的历史消息数量"
              >
                <Input type="number" min={1} max={50} />
              </Form.Item>
            </Card>

            {/* 项目配置 */}
            <Card title="项目配置" className="mt-6">
              <Form.Item
                label="自动刷新"
                name="auto_refresh"
              >
                <Radio.Group>
                  <Radio.Button value={true}>启用</Radio.Button>
                  <Radio.Button value={false}>禁用</Radio.Button>
                </Radio.Group>
              </Form.Item>

              <Form.Item
                label="刷新间隔 (毫秒)"
                name="refresh_interval"
                tooltip="项目列表自动刷新的时间间隔"
              >
                <Input type="number" min={5000} max={300000} />
              </Form.Item>
            </Card>

            {/* 操作按钮 */}
            <Form.Item className="mt-6 mb-0">
              <div className="flex gap-4">
                <Button
                  icon={<CheckCircleOutlined />}
                  onClick={handleTest}
                  loading={testing}
                >
                  测试连接
                </Button>
                <Button
                  type="primary"
                  icon={<SaveOutlined />}
                  htmlType="submit"
                  loading={loading}
                >
                  保存配置
                </Button>
              </div>
            </Form.Item>
          </Form>
        </Card>
      </div>
    </div>
  )
}

export default ConfigPage
