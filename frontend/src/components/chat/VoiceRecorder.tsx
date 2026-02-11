import React, { useState, useRef } from 'react'

export const testAudioFormats = () => {
  const testFormats = [
    'audio/wav',
    'audio/wave',
    'audio/x-wav',
    'audio/pcm',
    'audio/webm;codecs=opus',
    'audio/webm;codecs=pcm',
    'audio/ogg;codecs=opus',
  ]

  console.log('测试浏览器支持的音频格式:')
  testFormats.forEach(format => {
    const supported = MediaRecorder.isTypeSupported(format)
    console.log(`${format}: ${supported ? '✓ 支持' : '✗ 不支持'}`)
  })
}

export const getBestAudioFormat = (): string | null => {
  const formats = [
    'audio/wav',
    'audio/wave',
    'audio/x-wav',
    'audio/pcm',
    'audio/webm;codecs=opus',
    'audio/webm',
  ]

  for (const format of formats) {
    if (MediaRecorder.isTypeSupported(format)) {
      console.log(`选择音频格式: ${format}`)
      return format
    }
  }

  return null
}

export const startVoiceRecording = async (
  onDataAvailable: (data: Blob) => void,
  onStop: () => void,
  onError: (error: string) => void
) => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

    const mimeType = getBestAudioFormat() || 'audio/webm'
    console.log(`使用 mimeType: ${mimeType}`)

    const mediaRecorder = new MediaRecorder(stream, { mimeType })
    const chunks: Blob[] = []

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        console.log(`收到音频数据: ${event.data.size} bytes, type: ${event.data.type}`)
        chunks.push(event.data)
        onDataAvailable(event.data)
      }
    }

    mediaRecorder.onstop = () => {
      console.log(`录音结束，共收到 ${chunks.length} 个片段`)
      onStop()
    }

    mediaRecorder.onerror = (event) => {
      console.error('录音错误:', event)
      onError('录音发生错误')
    }

    mediaRecorder.start(200)

    return () => {
      mediaRecorder.stop()
      stream.getTracks().forEach(track => track.stop())
    }
  } catch (error) {
    console.error('无法访问麦克风:', error)
    onError('无法访问麦克风')
    return () => {}
  }
}

export const combineAudioBlobs = (blobs: Blob[]): Blob => {
  console.log(`合并 ${blobs.length} 个音频片段`)

  if (blobs.length === 0) {
    return new Blob([], { type: 'audio/webm' })
  }

  if (blobs.length === 1) {
    return blobs[0]
  }

  const blob = new Blob(blobs, { type: 'audio/webm' })
  console.log(`合并后大小: ${blob.size} bytes`)
  return blob
}

export const createWavHeader = (
  dataSize: number,
  sampleRate: number = 16000,
  channels: number = 1,
  bitsPerSample: number = 16
): ArrayBuffer => {
  const byteRate = sampleRate * channels * bitsPerSample / 8
  const blockAlign = channels * bitsPerSample / 8
  const buffer = new ArrayBuffer(44)
  const view = new DataView(buffer)

  let offset = 0

  const writeString = (str: string) => {
    for (let i = 0; i < str.length; i++) {
      view.setUint8(offset++, str.charCodeAt(i))
    }
  }

  writeString('RIFF')
  offset += 4
  view.setUint32(offset, 36 + dataSize, true)
  offset += 4
  writeString('WAVEfmt ')
  offset += 8
  view.setUint16(offset, 16, true)
  offset += 2
  view.setUint16(offset, 1, true)
  offset += 2
  view.setUint16(offset, channels, true)
  offset += 2
  view.setUint32(offset, sampleRate, true)
  offset += 4
  view.setUint32(offset, byteRate, true)
  offset += 4
  view.setUint16(offset, blockAlign, true)
  offset += 2
  view.setUint16(offset, bitsPerSample, true)
  offset += 2
  writeString('data')
  offset += 4
  view.setUint32(offset, dataSize, true)

  return buffer
}

export const blobToWav = async (blob: Blob): Promise<Blob> => {
  const arrayBuffer = await blob.arrayBuffer()
  const data = new Uint8Array(arrayBuffer)

  const wavHeader = createWavHeader(data.length)
  const wavBlob = new Blob([wavHeader, data], { type: 'audio/wav' })

  console.log(`转换为WAV: 原始 ${data.length} bytes, 转换后 ${wavBlob.size} bytes`)
  return wavBlob
}
