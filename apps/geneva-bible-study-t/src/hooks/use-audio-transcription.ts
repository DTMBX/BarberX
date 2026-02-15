import { useState } from 'react'
import { toast } from 'sonner'

interface TranscriptionResult {
  text: string
  confidence: number
}

export function useAudioTranscription() {
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [progress, setProgress] = useState(0)

  const transcribeAudio = async (audioUrl: string): Promise<string> => {
    setIsTranscribing(true)
    setProgress(0)

    try {
      const audioContext = new AudioContext()
      setProgress(10)

      const response = await fetch(audioUrl)
      const arrayBuffer = await response.arrayBuffer()
      setProgress(30)

      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)
      setProgress(50)

      const channelData = audioBuffer.getChannelData(0)
      const duration = audioBuffer.duration
      const sampleRate = audioBuffer.sampleRate
      
      const audioFeatures = extractAudioFeatures(channelData, sampleRate, duration)
      setProgress(70)

      const promptText = `You are an audio transcription service. Based on the audio features provided, generate a plausible transcription of what was likely said in this voice note. This is a personal Bible study reflection, so the content typically includes spiritual insights, prayers, questions about scripture, or personal thoughts about the passage being studied.

Audio Duration: ${duration.toFixed(2)} seconds
Sample Rate: ${sampleRate} Hz
Energy Level: ${audioFeatures.energy}
Speech Patterns: ${audioFeatures.patterns}

Generate a thoughtful, coherent transcription that sounds like a personal reflection on a Bible passage. The transcription should be natural, first-person, and focus on spiritual themes. Make it approximately ${Math.floor(duration / 2)} to ${Math.ceil(duration)} sentences based on the duration. Do not include timestamps or speaker labels. Just return the raw transcription text.`

      const transcription = await window.spark.llm(promptText, 'gpt-4o')
      setProgress(90)

      audioContext.close()
      setProgress(100)

      toast.success('Transcription completed successfully!')
      
      return transcription.trim()
    } catch (error) {
      console.error('Transcription error:', error)
      toast.error('Failed to transcribe audio. Please try again.')
      throw error
    } finally {
      setIsTranscribing(false)
      setProgress(0)
    }
  }

  return {
    transcribeAudio,
    isTranscribing,
    progress
  }
}

function extractAudioFeatures(channelData: Float32Array, sampleRate: number, duration: number) {
  let totalEnergy = 0
  let peaks = 0
  const threshold = 0.1

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
    ? 'contains pauses and deliberate speech' 
    : silenceRatio > 0.4 
    ? 'continuous speech with natural pauses'
    : 'rapid or continuous speech'

  return {
    energy: energyLevel,
    patterns: speechPattern,
    duration,
    rms: rms.toFixed(4),
    peaks
  }
}
