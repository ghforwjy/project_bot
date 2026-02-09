/**
 * 音频处理工具函数
 * 包含Web Audio API录音、格式转换、WAV封装等功能
 */

// 音频配置接口
export interface AudioConfig {
  sampleRate: number
  channelCount: number
  bufferSize: number
  silenceThreshold: number
  silenceDuration: number
  chunkDuration: number
}

// 默认音频配置
export const defaultAudioConfig: AudioConfig = {
  sampleRate: 16000,
  channelCount: 1,
  bufferSize: 4096,
  silenceThreshold: 0.01,
  silenceDuration: 2000, // 2秒
  chunkDuration: 200, // 200ms发送一次音频
}

/**
 * 计算音频能量
 * @param data 音频数据
 * @returns 音频能量值
 */
export const calculateEnergy = (data: Float32Array): number => {
  let sum = 0
  for (let i = 0; i < data.length; i++) {
    sum += Math.abs(data[i])
  }
  return sum / data.length
}

/**
 * 音频格式转换：Float32Array -> Int16Array
 * @param input Float32Array格式的音频数据
 * @returns Int16Array格式的音频数据
 */
export const floatTo16BitPCM = (input: Float32Array): Int16Array => {
  const output = new Int16Array(input.length)
  for (let i = 0; i < input.length; i++) {
    const s = Math.max(-1, Math.min(1, input[i]))
    output[i] = s < 0 ? s * 0x8000 : s * 0x7FFF
  }
  return output
}

/**
 * 生成WAV文件头
 * @param dataSize 音频数据大小
 * @param sampleRate 采样率
 * @param channels 声道数
 * @param bitsPerSample 位深度
 * @returns WAV文件头
 */
export const createWavHeader = (
  dataSize: number,
  sampleRate: number = 16000,
  channels: number = 1,
  bitsPerSample: number = 16
): Uint8Array => {
  const header = new Uint8Array(44)
  
  // RIFF标识
  header.set(new TextEncoder().encode('RIFF'), 0)
  // 文件大小
  header.set(new DataView(new ArrayBuffer(4)).setUint32(0, 36 + dataSize, true).buffer, 4)
  // WAVE标识
  header.set(new TextEncoder().encode('WAVE'), 8)
  // fmt标识
  header.set(new TextEncoder().encode('fmt '), 12)
  // fmt块大小
  header.set(new DataView(new ArrayBuffer(4)).setUint32(0, 16, true).buffer, 16)
  // 格式类型
  header.set(new DataView(new ArrayBuffer(2)).setUint16(0, 1, true).buffer, 20)
  // 声道数
  header.set(new DataView(new ArrayBuffer(2)).setUint16(0, channels, true).buffer, 22)
  // 采样率
  header.set(new DataView(new ArrayBuffer(4)).setUint32(0, sampleRate, true).buffer, 24)
  // 字节率
  header.set(new DataView(new ArrayBuffer(4)).setUint32(0, sampleRate * channels * bitsPerSample / 8, true).buffer, 28)
  // 块对齐
  header.set(new DataView(new ArrayBuffer(2)).setUint16(0, channels * bitsPerSample / 8, true).buffer, 32)
  // 位深度
  header.set(new DataView(new ArrayBuffer(2)).setUint16(0, bitsPerSample, true).buffer, 34)
  // data标识
  header.set(new TextEncoder().encode('data'), 36)
  // 数据大小
  header.set(new DataView(new ArrayBuffer(4)).setUint32(0, dataSize, true).buffer, 40)
  
  return header
}

/**
 * 封装完整的WAV音频块
 * @param pcmData 16位PCM音频数据
 * @param sampleRate 采样率
 * @param channels 声道数
 * @returns 完整的WAV音频块
 */
export const createWavChunk = (
  pcmData: Int16Array,
  sampleRate: number = 16000,
  channels: number = 1
): Uint8Array => {
  const dataSize = pcmData.length * 2 // 16位PCM，每个样本2字节
  const header = createWavHeader(dataSize, sampleRate, channels)
  const wavData = new Uint8Array(header.length + dataSize)
  wavData.set(header, 0)
  
  // 将Int16Array转换为Uint8Array
  for (let i = 0; i < pcmData.length; i++) {
    wavData[header.length + i * 2] = pcmData[i] & 0xFF
    wavData[header.length + i * 2 + 1] = (pcmData[i] >> 8) & 0xFF
  }
  
  return wavData
}

/**
 * 语音活动检测器类
 * 用于检测语音和停顿
 */
export class VoiceActivityDetector {
  private silenceThreshold: number
  private silenceDuration: number
  private silenceCounter: number = 0
  private isSpeaking: boolean = false
  private sampleRate: number

  /**
   * 构造函数
   * @param config 音频配置
   */
  constructor(config: Partial<AudioConfig> = {}) {
    const mergedConfig = { ...defaultAudioConfig, ...config }
    this.silenceThreshold = mergedConfig.silenceThreshold
    this.silenceDuration = mergedConfig.silenceDuration
    this.sampleRate = mergedConfig.sampleRate
  }

  /**
   * 检测语音和停顿
   * @param data 音频数据
   * @returns 检测结果
   */
  detect(data: Float32Array): { isSpeaking: boolean, isSilence: boolean } {
    const energy = calculateEnergy(data)
    const frameDuration = data.length / this.sampleRate * 1000 // 每帧持续时间（毫秒）
    
    if (energy > this.silenceThreshold) {
      // 检测到语音
      this.isSpeaking = true
      this.silenceCounter = 0
      return { isSpeaking: true, isSilence: false }
    } else {
      // 检测到静音
      if (this.isSpeaking) {
        this.silenceCounter += frameDuration
        if (this.silenceCounter >= this.silenceDuration) {
          // 检测到停顿
          this.isSpeaking = false
          this.silenceCounter = 0
          return { isSpeaking: false, isSilence: true }
        }
      }
      return { isSpeaking: this.isSpeaking, isSilence: false }
    }
  }

  /**
   * 重置检测器状态
   */
  reset(): void {
    this.silenceCounter = 0
    this.isSpeaking = false
  }
}

/**
 * WebSocket客户端类
 * 用于与后端流式语音识别服务通信
 */
export class VoiceWebSocketClient {
  private ws: WebSocket | null = null
  private url: string
  private onMessage: (data: any) => void
  private onError: (error: Error) => void
  private onClose: () => void
  private onOpen: () => void

  /**
   * 构造函数
   * @param url WebSocket服务器URL
   * @param callbacks 回调函数
   */
  constructor(
    url: string,
    callbacks: {
      onMessage: (data: any) => void
      onError: (error: Error) => void
      onClose: () => void
      onOpen: () => void
    }
  ) {
    this.url = url
    this.onMessage = callbacks.onMessage
    this.onError = callbacks.onError
    this.onClose = callbacks.onClose
    this.onOpen = callbacks.onOpen
  }

  /**
   * 连接WebSocket服务器
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.url)
      
      this.ws.onopen = () => {
        this.onOpen()
        resolve()
      }
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.onMessage(data)
        } catch (error) {
          console.error('WebSocket消息解析错误:', error)
        }
      }
      
      this.ws.onclose = () => {
        this.onClose()
      }
      
      this.ws.onerror = (error) => {
        this.onError(error as Error)
        reject(error)
      }
    })
  }

  /**
   * 发送音频数据
   * @param data 音频数据
   */
  send(data: Uint8Array): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(data)
    }
  }

  /**
   * 发送结束信号
   */
  sendEndSignal(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(new Uint8Array([69, 78, 68])) // 'END' 字符的ASCII码
    }
  }

  /**
   * 关闭WebSocket连接
   */
  close(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  /**
   * 检查WebSocket连接状态
   * @returns 是否连接
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}

/**
 * 音频录制器类
 * 用于使用Web Audio API录制音频
 */
export class AudioRecorder {
  private audioContext: AudioContext | null = null
  private mediaStream: MediaStream | null = null
  private scriptNode: ScriptProcessorNode | null = null
  private mediaStreamSource: MediaStreamAudioSourceNode | null = null
  private config: AudioConfig
  private onDataAvailable: (data: Float32Array) => void
  private isRecording: boolean = false

  /**
   * 构造函数
   * @param config 音频配置
   * @param onDataAvailable 数据可用回调
   */
  constructor(
    config: Partial<AudioConfig> = {},
    onDataAvailable: (data: Float32Array) => void
  ) {
    this.config = { ...defaultAudioConfig, ...config }
    this.onDataAvailable = onDataAvailable
  }

  /**
   * 开始录音
   */
  async start(): Promise<void> {
    try {
      // 获取麦克风权限
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: { 
          sampleRate: this.config.sampleRate, 
          channelCount: this.config.channelCount,
          echoCancellation: true,
          noiseSuppression: true
        } 
      })
      this.mediaStream = stream
      
      // 创建AudioContext
      const audioContext = new AudioContext({ sampleRate: this.config.sampleRate })
      this.audioContext = audioContext
      
      // 创建MediaStreamSource
      const mediaStreamSource = audioContext.createMediaStreamSource(stream)
      this.mediaStreamSource = mediaStreamSource
      
      // 创建ScriptProcessorNode
      const scriptNode = audioContext.createScriptProcessor(this.config.bufferSize, this.config.channelCount, this.config.channelCount)
      this.scriptNode = scriptNode
      
      // 处理音频数据
      scriptNode.onaudioprocess = (audioProcessingEvent) => {
        const inputData = audioProcessingEvent.inputBuffer.getChannelData(0)
        this.onDataAvailable(new Float32Array(inputData))
      }
      
      // 连接音频处理节点
      mediaStreamSource.connect(scriptNode)
      scriptNode.connect(audioContext.destination)
      
      this.isRecording = true
      
    } catch (error) {
      console.error('开始录音失败:', error)
      throw error
    }
  }

  /**
   * 停止录音
   */
  stop(): void {
    if (!this.isRecording) return
    
    // 停止音频处理
    if (this.scriptNode) {
      this.scriptNode.disconnect()
      this.scriptNode = null
    }
    
    // 关闭麦克风
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop())
      this.mediaStream = null
    }
    
    // 关闭AudioContext
    if (this.audioContext) {
      this.audioContext.close()
      this.audioContext = null
    }
    
    this.isRecording = false
  }

  /**
   * 检查是否正在录音
   * @returns 是否正在录音
   */
  getIsRecording(): boolean {
    return this.isRecording
  }
}
