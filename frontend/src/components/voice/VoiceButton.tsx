import React, { useState, useRef, useEffect, forwardRef, useImperativeHandle } from 'react'
import { Button, message, Tooltip } from 'antd'
import { AudioOutlined, StopOutlined, LoadingOutlined } from '@ant-design/icons'

interface VoiceButtonProps {
  onVoiceResult: (text: string) => void
  isDisabled?: boolean
}

interface VoiceButtonRef {
  stopRecording: () => void
  isRecording: boolean
}

const VoiceButton = forwardRef<VoiceButtonRef, VoiceButtonProps>(({ onVoiceResult, isDisabled = false }, ref) => {
  const [isRecording, setIsRecording] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // 音频处理相关引用
  const audioContextRef = useRef<AudioContext | null>(null)
  const mediaStreamRef = useRef<MediaStream | null>(null)
  const scriptNodeRef = useRef<ScriptProcessorNode | null>(null)
  const websocketRef = useRef<WebSocket | null>(null)
  const audioBufferRef = useRef<Float32Array[]>([])
  const silenceCounterRef = useRef(0)
  const isSpeakingRef = useRef(false)
  
  // 通过 ref 暴露方法和状态
  useImperativeHandle(ref, () => ({
    stopRecording,
    isRecording
  }))
  
  // 配置参数
  const config = {
    sampleRate: 16000,
    channelCount: 1,
    bufferSize: 4096,
    silenceThreshold: 0.01,
    silenceDuration: 2000, // 2秒
    chunkDuration: 200, // 200ms发送一次音频
  }

  // 计算音频能量
  const calculateEnergy = (data: Float32Array): number => {
    let sum = 0
    for (let i = 0; i < data.length; i++) {
      sum += Math.abs(data[i])
    }
    return sum / data.length
  }

  // 音频格式转换：Float32Array -> Int16Array
  const floatTo16BitPCM = (input: Float32Array): Int16Array => {
    const output = new Int16Array(input.length)
    for (let i = 0; i < input.length; i++) {
      const s = Math.max(-1, Math.min(1, input[i]))
      output[i] = s < 0 ? s * 0x8000 : s * 0x7FFF
    }
    return output
  }

  // 生成WAV文件头
  const createWavHeader = (dataSize: number): Uint8Array => {
    const header = new Uint8Array(44)
    const sampleRate = config.sampleRate
    const channels = config.channelCount
    const bitsPerSample = 16
    
    // RIFF标识
    header.set(new TextEncoder().encode('RIFF'), 0)
    // 文件大小
    const fileSizeBuffer = new ArrayBuffer(4)
    const fileSizeView = new DataView(fileSizeBuffer)
    fileSizeView.setUint32(0, 36 + dataSize, true)
    header.set(new Uint8Array(fileSizeBuffer), 4)
    // WAVE标识
    header.set(new TextEncoder().encode('WAVE'), 8)
    // fmt标识
    header.set(new TextEncoder().encode('fmt '), 12)
    // fmt块大小
    const fmtSizeBuffer = new ArrayBuffer(4)
    const fmtSizeView = new DataView(fmtSizeBuffer)
    fmtSizeView.setUint32(0, 16, true)
    header.set(new Uint8Array(fmtSizeBuffer), 16)
    // 格式类型
    const formatBuffer = new ArrayBuffer(2)
    const formatView = new DataView(formatBuffer)
    formatView.setUint16(0, 1, true)
    header.set(new Uint8Array(formatBuffer), 20)
    // 声道数
    const channelsBuffer = new ArrayBuffer(2)
    const channelsView = new DataView(channelsBuffer)
    channelsView.setUint16(0, channels, true)
    header.set(new Uint8Array(channelsBuffer), 22)
    // 采样率
    const sampleRateBuffer = new ArrayBuffer(4)
    const sampleRateView = new DataView(sampleRateBuffer)
    sampleRateView.setUint32(0, sampleRate, true)
    header.set(new Uint8Array(sampleRateBuffer), 24)
    // 字节率
    const byteRateBuffer = new ArrayBuffer(4)
    const byteRateView = new DataView(byteRateBuffer)
    byteRateView.setUint32(0, sampleRate * channels * bitsPerSample / 8, true)
    header.set(new Uint8Array(byteRateBuffer), 28)
    // 块对齐
    const blockAlignBuffer = new ArrayBuffer(2)
    const blockAlignView = new DataView(blockAlignBuffer)
    blockAlignView.setUint16(0, channels * bitsPerSample / 8, true)
    header.set(new Uint8Array(blockAlignBuffer), 32)
    // 位深度
    const bitsPerSampleBuffer = new ArrayBuffer(2)
    const bitsPerSampleView = new DataView(bitsPerSampleBuffer)
    bitsPerSampleView.setUint16(0, bitsPerSample, true)
    header.set(new Uint8Array(bitsPerSampleBuffer), 34)
    // data标识
    header.set(new TextEncoder().encode('data'), 36)
    // 数据大小
    const dataSizeBuffer = new ArrayBuffer(4)
    const dataSizeView = new DataView(dataSizeBuffer)
    dataSizeView.setUint32(0, dataSize, true)
    header.set(new Uint8Array(dataSizeBuffer), 40)
    
    return header
  }

  // 封装完整的WAV音频块
  const createWavChunk = (pcmData: Int16Array): Uint8Array => {
    const dataSize = pcmData.length * 2 // 16位PCM，每个样本2字节
    const header = createWavHeader(dataSize)
    const wavData = new Uint8Array(header.length + dataSize)
    wavData.set(header, 0)
    
    // 将Int16Array转换为Uint8Array
    for (let i = 0; i < pcmData.length; i++) {
      wavData[header.length + i * 2] = pcmData[i] & 0xFF
      wavData[header.length + i * 2 + 1] = (pcmData[i] >> 8) & 0xFF
    }
    
    return wavData
  }

  // 初始化WebSocket连接
  const initWebSocket = (): WebSocket => {
    const ws = new WebSocket('ws://localhost:8000/api/v1/voice/stream')
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'recognition_result') {
          onVoiceResult(data.text)
        } else if (data.type === 'error') {
          setError(data.message)
          message.error(`语音识别错误: ${data.message}`)
          stopRecording()
        }
      } catch (error) {
        console.error('WebSocket消息解析错误:', error)
      }
    }
    
    ws.onclose = () => {
      console.log('WebSocket连接已关闭')
      setIsConnecting(false)
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket错误:', error)
      setError('WebSocket连接错误')
      message.error('WebSocket连接错误')
      setIsConnecting(false)
      stopRecording()
    }
    
    return ws
  }

  // 开始录音
  const startRecording = async () => {
    if (isDisabled) return
    
    try {
      setIsConnecting(true)
      setError(null)
      
      // 初始化WebSocket连接
      const ws = initWebSocket()
      websocketRef.current = ws
      
      // 等待WebSocket连接建立
      await new Promise((resolve, reject) => {
        const timeout = setTimeout(() => reject(new Error('WebSocket连接超时')), 5000)
        ws.onopen = () => {
          clearTimeout(timeout)
          console.log('WebSocket连接已建立')
          setIsConnecting(false)
          resolve(true)
        }
        ws.onerror = (error) => {
          clearTimeout(timeout)
          setIsConnecting(false)
          reject(error)
        }
      })
      
      // 获取麦克风权限
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: { 
          sampleRate: config.sampleRate, 
          channelCount: config.channelCount,
          echoCancellation: true,
          noiseSuppression: true
        } 
      })
      mediaStreamRef.current = stream
      
      // 创建AudioContext
      const audioContext = new AudioContext({ sampleRate: config.sampleRate })
      audioContextRef.current = audioContext
      
      // 创建MediaStreamSource
      const mediaStreamSource = audioContext.createMediaStreamSource(stream)
      
      // 创建ScriptProcessorNode
      const scriptNode = audioContext.createScriptProcessor(config.bufferSize, config.channelCount, config.channelCount)
      scriptNodeRef.current = scriptNode
      
      // 音频数据缓冲区
      let audioBuffer: Float32Array[] = []
      let chunkCounter = 0
      const samplesPerChunk = config.sampleRate * config.chunkDuration / 1000
      
      // 处理音频数据
      scriptNode.onaudioprocess = (audioProcessingEvent) => {
        const inputData = audioProcessingEvent.inputBuffer.getChannelData(0)
        
        // 计算音频能量
        const energy = calculateEnergy(inputData)
        
        // 语音检测
        if (energy > config.silenceThreshold) {
          isSpeakingRef.current = true
          silenceCounterRef.current = 0
        } else {
          if (isSpeakingRef.current) {
            silenceCounterRef.current += inputData.length / config.sampleRate * 1000
            if (silenceCounterRef.current >= config.silenceDuration) {
              // 检测到停顿，停止录音
              console.log('检测到语音停顿，停止录音')
              stopRecording()
              return
            }
          }
        }
        
        // 收集音频数据
        audioBuffer.push(new Float32Array(inputData))
        chunkCounter += inputData.length
        
        // 每累积一定量的音频数据，发送一次
        if (chunkCounter >= samplesPerChunk) {
          // 合并音频数据
          const combinedData = new Float32Array(chunkCounter)
          let offset = 0
          for (const buffer of audioBuffer) {
            combinedData.set(buffer, offset)
            offset += buffer.length
          }
          
          // 转换为16位PCM
          const pcmData = floatTo16BitPCM(combinedData)
          
          // 封装为WAV格式
          const wavData = createWavChunk(pcmData)
          
          // 发送音频数据
          if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
            websocketRef.current.send(wavData)
          }
          
          // 重置缓冲区
          audioBuffer = []
          chunkCounter = 0
        }
      }
      
      // 连接音频处理节点
      mediaStreamSource.connect(scriptNode)
      scriptNode.connect(audioContext.destination)
      
      setIsRecording(true)
      message.success('开始录音')
      
    } catch (error) {
      console.error('开始录音失败:', error)
      setError('开始录音失败')
      message.error('开始录音失败，请检查麦克风权限')
      setIsConnecting(false)
      stopRecording()
    }
  }

  // 停止录音
  const stopRecording = () => {
    if (!isRecording) return
    
    try {
      setIsRecording(false)
      
      // 停止音频处理
      if (scriptNodeRef.current) {
        try {
          scriptNodeRef.current.disconnect()
        } catch (error) {
          console.error('停止音频处理失败:', error)
        }
        scriptNodeRef.current = null
      }
      
      // 关闭麦克风
      if (mediaStreamRef.current) {
        try {
          mediaStreamRef.current.getTracks().forEach(track => {
            try {
              track.stop()
            } catch (error) {
              console.error('停止麦克风轨道失败:', error)
            }
          })
        } catch (error) {
          console.error('关闭麦克风失败:', error)
        }
        mediaStreamRef.current = null
      }
      
      // 关闭AudioContext
      if (audioContextRef.current) {
        try {
          audioContextRef.current.close()
        } catch (error) {
          console.error('关闭AudioContext失败:', error)
        }
        audioContextRef.current = null
      }
      
      // 发送结束信号
      if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
        try {
          websocketRef.current.send(new Uint8Array([69, 78, 68])) // 'END' 字符的ASCII码
          
          // 延迟关闭WebSocket，确保所有数据都已发送
          setTimeout(() => {
            if (websocketRef.current) {
              try {
                websocketRef.current.close()
              } catch (error) {
                console.error('关闭WebSocket失败:', error)
              }
              websocketRef.current = null
            }
          }, 500)
        } catch (error) {
          console.error('发送结束信号失败:', error)
        }
      }
      
      message.success('录音已停止')
    } catch (error) {
      console.error('停止录音失败:', error)
      message.error('停止录音失败')
    }
  }

  // 清理函数
  useEffect(() => {
    return () => {
      stopRecording()
    }
  }, [])

  return (
    <Tooltip title={isRecording ? "停止录音" : "开始录音"}>
      <Button
        type="primary"
        icon={isConnecting ? <LoadingOutlined /> : isRecording ? <StopOutlined /> : <AudioOutlined />}
        onClick={isRecording ? stopRecording : startRecording}
        disabled={isDisabled || isConnecting}
        style={{ width: 40, height: 40 }}
      />

    </Tooltip>
  )
})

VoiceButton.displayName = 'VoiceButton'

export default VoiceButton
