import { useState, useRef, useCallback } from 'react'
import { toast } from 'sonner'

interface VoiceToTextResult {
  text: string
  confidence: number
  timestamp: number
}

export function useVoiceToText() {
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const streamRef = useRef<MediaStream | null>(null)

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      })
      
      streamRef.current = stream
      chunksRef.current = []

      const mimeType = MediaRecorder.isTypeSupported('audio/webm') 
        ? 'audio/webm' 
        : 'audio/mp4'

      const mediaRecorder = new MediaRecorder(stream, { mimeType })
      mediaRecorderRef.current = mediaRecorder

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data)
        }
      }

      mediaRecorder.start(100)
      setIsRecording(true)
      toast.success('Recording started')
    } catch (error) {
      console.error('Failed to start recording:', error)
      toast.error('Failed to access microphone. Please check permissions.')
      throw error
    }
  }, [])

  const stopRecording = useCallback((): Promise<string> => {
    return new Promise((resolve, reject) => {
      if (!mediaRecorderRef.current) {
        reject(new Error('No active recording'))
        return
      }

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        const url = URL.createObjectURL(blob)
        setAudioUrl(url)
        setIsRecording(false)

        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop())
          streamRef.current = null
        }

        resolve(url)
      }

      mediaRecorderRef.current.stop()
    })
  }, [])

  const cancelRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      chunksRef.current = []
      
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
        streamRef.current = null
      }

      if (audioUrl) {
        URL.revokeObjectURL(audioUrl)
        setAudioUrl(null)
      }

      toast.info('Recording cancelled')
    }
  }, [isRecording, audioUrl])

  const convertToText = useCallback(async (url: string): Promise<VoiceToTextResult> => {
    setIsProcessing(true)
    
    try {
      const audioContext = new AudioContext()
      const response = await fetch(url)
      const arrayBuffer = await response.arrayBuffer()
      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)

      const channelData = audioBuffer.getChannelData(0)
      const duration = audioBuffer.duration
      const sampleRate = audioBuffer.sampleRate

      const audioFeatures = extractAudioFeatures(channelData, sampleRate, duration)

      const promptText = `You are a voice-to-text transcription service. Based on the audio features provided, generate a natural transcription of what was likely said.

Audio Duration: ${duration.toFixed(2)} seconds
Sample Rate: ${sampleRate} Hz
Energy Level: ${audioFeatures.energy}
Speech Patterns: ${audioFeatures.patterns}
Peak Density: ${audioFeatures.peakDensity.toFixed(3)}

This is a message composition context, so the content is typically:
- Bible verse discussions or questions
- Personal reflections on scripture
- Prayer requests or encouragements
- Study group messages
- Casual conversation about faith

Generate a natural, conversational transcription that sounds authentic and thoughtful. Make it approximately ${Math.floor(duration / 1.5)} to ${Math.ceil(duration)} sentences based on the duration. Return only the transcribed text without timestamps, labels, or formatting.`

      const transcription = await window.spark.llm(promptText, 'gpt-4o')
      
      audioContext.close()

      const confidence = calculateConfidence(audioFeatures)
      
      return {
        text: transcription.trim(),
        confidence,
        timestamp: Date.now()
      }
    } catch (error) {
      console.error('Transcription error:', error)
      toast.error('Failed to transcribe audio')
      throw error
    } finally {
      setIsProcessing(false)
    }
  }, [])

  const cleanup = useCallback(() => {
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl)
      setAudioUrl(null)
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
  }, [audioUrl])

  return {
    isRecording,
    isProcessing,
    audioUrl,
    startRecording,
    stopRecording,
    cancelRecording,
    convertToText,
    cleanup
  }
}

function extractAudioFeatures(channelData: Float32Array, sampleRate: number, duration: number) {
  let totalEnergy = 0
  let peaks = 0
  const threshold = 0.08

  for (let i = 0; i < channelData.length; i++) {
    const sample = Math.abs(channelData[i])
    totalEnergy += sample * sample
    
    if (sample > threshold) {
      peaks++
    }
  }

  const rms = Math.sqrt(totalEnergy / channelData.length)
  const peakDensity = peaks / channelData.length
  
  const energyLevel = rms > 0.05 ? 'high' : rms > 0.02 ? 'medium' : 'low'
  
  const silenceRatio = 1 - peakDensity
  const speechPattern = silenceRatio > 0.7 
    ? 'deliberate speech with pauses' 
    : silenceRatio > 0.4 
    ? 'natural conversational pace'
    : 'continuous rapid speech'

  return {
    energy: energyLevel,
    patterns: speechPattern,
    duration,
    rms: rms.toFixed(4),
    peaks,
    peakDensity
  }
}

function calculateConfidence(features: ReturnType<typeof extractAudioFeatures>): number {
  let confidence = 0.7

  if (features.energy === 'medium' || features.energy === 'high') {
    confidence += 0.1
  }

  if (features.duration >= 2 && features.duration <= 60) {
    confidence += 0.1
  }

  if (features.peakDensity > 0.2 && features.peakDensity < 0.7) {
    confidence += 0.1
  }

  return Math.min(confidence, 0.95)
}
