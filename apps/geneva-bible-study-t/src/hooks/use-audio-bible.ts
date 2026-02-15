import { useState, useEffect, useRef, useCallback } from 'react'
import { useKV } from '@github/spark/hooks'
import type { AudioNarrator, AudioPlaybackState, AudioPreferences, VerseUnit, AudioPlaylist } from '@/lib/types'

export function useAvailableVoices() {
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([])

  useEffect(() => {
    const loadVoices = () => {
      const availableVoices = window.speechSynthesis.getVoices()
      setVoices(availableVoices)
    }

    loadVoices()
    window.speechSynthesis.onvoiceschanged = loadVoices

    return () => {
      window.speechSynthesis.onvoiceschanged = null
    }
  }, [])

  return voices
}

export function useAudioNarrators(): AudioNarrator[] {
  const voices = useAvailableVoices()

  const usVoices = voices.filter(v => v.lang.startsWith('en-US') || v.lang.startsWith('en_US'))
  const gbVoices = voices.filter(v => v.lang.startsWith('en-GB') || v.lang.startsWith('en_GB'))
  const auVoices = voices.filter(v => v.lang.startsWith('en-AU') || v.lang.startsWith('en_AU'))
  const otherEnVoices = voices.filter(v => v.lang.startsWith('en') && !v.lang.startsWith('en-US') && !v.lang.startsWith('en-GB') && !v.lang.startsWith('en-AU'))

  const maleNames = ['david', 'daniel', 'james', 'thomas', 'george', 'alex', 'fred', 'paul', 'john', 'michael', 'aaron', 'arthur', 'bruce', 'oliver', 'william', 'nathan', 'samuel', 'timothy', 'matthew']
  const femaleNames = ['samantha', 'victoria', 'karen', 'sarah', 'kate', 'anna', 'susan', 'zoe', 'fiona', 'moira', 'catherine', 'elizabeth', 'alice', 'jessica', 'nicole', 'natalie', 'emily', 'emma']

  const isLikelyMale = (voice: SpeechSynthesisVoice) => {
    const name = voice.name.toLowerCase()
    return maleNames.some(n => name.includes(n)) || name.includes('male')
  }

  const isLikelyFemale = (voice: SpeechSynthesisVoice) => {
    const name = voice.name.toLowerCase()
    return femaleNames.some(n => name.includes(n)) || name.includes('female')
  }

  const getVoicesByGender = (voiceList: SpeechSynthesisVoice[], preferMale: boolean) => {
    const gendered = voiceList.filter(v => preferMale ? isLikelyMale(v) : isLikelyFemale(v))
    return gendered.length > 0 ? gendered : voiceList
  }

  const pickUnique = (voiceList: SpeechSynthesisVoice[], usedVoices: SpeechSynthesisVoice[]) => {
    const unused = voiceList.filter(v => !usedVoices.includes(v))
    return unused.length > 0 ? unused[0] : voiceList[0]
  }

  const usedVoices: SpeechSynthesisVoice[] = []

  const usMaleVoices = getVoicesByGender(usVoices, true)
  const usMale = usMaleVoices[0] || usVoices[0] || voices[0] || null
  if (usMale) usedVoices.push(usMale)

  const usFemaleVoices = getVoicesByGender(usVoices, false)
  const usFemale = pickUnique(usFemaleVoices, usedVoices) || usVoices[Math.min(1, usVoices.length - 1)] || voices[0] || null
  if (usFemale) usedVoices.push(usFemale)

  const gbMaleVoices = getVoicesByGender(gbVoices, true)
  const gbMale = pickUnique(gbMaleVoices.length > 0 ? gbMaleVoices : [...gbVoices, ...usVoices], usedVoices)
  if (gbMale) usedVoices.push(gbMale)

  const gbFemaleVoices = getVoicesByGender(gbVoices, false)
  const gbFemale = pickUnique(gbFemaleVoices.length > 0 ? gbFemaleVoices : [...gbVoices, ...usVoices], usedVoices)
  if (gbFemale) usedVoices.push(gbFemale)

  const auMaleVoices = getVoicesByGender(auVoices, true)
  const auMale = pickUnique(auMaleVoices.length > 0 ? auMaleVoices : [...auVoices, ...usVoices], usedVoices)
  if (auMale) usedVoices.push(auMale)

  const auFemaleVoices = getVoicesByGender(auVoices, false)
  const auFemale = pickUnique(auFemaleVoices.length > 0 ? auFemaleVoices : [...auVoices, ...usVoices], usedVoices)
  if (auFemale) usedVoices.push(auFemale)

  const additionalVoices = [...otherEnVoices, ...usVoices, ...gbVoices, ...auVoices].filter(v => !usedVoices.includes(v))
  const extra1 = additionalVoices[0] || null
  if (extra1) usedVoices.push(extra1)

  const extra2 = additionalVoices[1] || null
  if (extra2) usedVoices.push(extra2)

  const narrators: AudioNarrator[] = [
    {
      id: 'david-american',
      name: 'David',
      description: 'Clear American male voice, excellent for study',
      gender: 'male',
      accent: 'american',
      voice: usMale,
      previewText: 'In the beginning God created the heaven and the earth.',
      quality: 'standard'
    },
    {
      id: 'sarah-american',
      name: 'Sarah',
      description: 'Warm American female voice, comforting tone',
      gender: 'female',
      accent: 'american',
      voice: usFemale,
      previewText: 'The Lord is my shepherd; I shall not want.',
      quality: 'standard'
    },
    {
      id: 'james-british',
      name: 'James',
      description: 'Distinguished British male voice, traditional reading',
      gender: 'male',
      accent: 'british',
      voice: gbMale,
      previewText: 'For God so loved the world, that he gave his only begotten Son.',
      quality: 'premium'
    },
    {
      id: 'elizabeth-british',
      name: 'Elizabeth',
      description: 'Elegant British female voice, refined reading',
      gender: 'female',
      accent: 'british',
      voice: gbFemale,
      previewText: 'Blessed are the pure in heart: for they shall see God.',
      quality: 'premium'
    },
    {
      id: 'nathan-australian',
      name: 'Nathan',
      description: 'Friendly Australian male voice, engaging delivery',
      gender: 'male',
      accent: 'australian',
      voice: auMale,
      previewText: 'Trust in the Lord with all thine heart and lean not unto thine own understanding.',
      quality: 'standard'
    },
    {
      id: 'olivia-australian',
      name: 'Olivia',
      description: 'Gentle Australian female voice, soothing tone',
      gender: 'female',
      accent: 'australian',
      voice: auFemale,
      previewText: 'The Lord is my light and my salvation; whom shall I fear?',
      quality: 'standard'
    },
    {
      id: 'voice-7',
      name: extra1?.name ? extra1.name.split(' ')[0] : 'Reader 7',
      description: 'Additional narrator option for variety',
      gender: isLikelyFemale(extra1 || voices[0]) ? 'female' : 'male',
      accent: extra1?.lang.includes('GB') ? 'british' : extra1?.lang.includes('AU') ? 'australian' : 'american',
      voice: extra1,
      previewText: 'The fear of the Lord is the beginning of wisdom.',
      quality: 'standard'
    },
    {
      id: 'voice-8',
      name: extra2?.name ? extra2.name.split(' ')[0] : 'Reader 8',
      description: 'Additional narrator option for variety',
      gender: isLikelyFemale(extra2 || voices[0]) ? 'female' : 'male',
      accent: extra2?.lang.includes('GB') ? 'british' : extra2?.lang.includes('AU') ? 'australian' : 'american',
      voice: extra2,
      previewText: 'Be strong and of good courage; be not afraid, neither be thou dismayed.',
      quality: 'standard'
    }
  ]

  return narrators.filter(n => n.voice !== null)
}

export function useAudioBible(verses: VerseUnit[], bookId?: string, chapter?: number) {
  const narrators = useAudioNarrators()
  const [audioPreferences, setAudioPreferences] = useKV<AudioPreferences>('audio-preferences', {
    defaultNarratorId: 'david-american',
    playbackRate: 1.0,
    volume: 0.8,
    autoAdvanceChapter: false,
    highlightCurrentVerse: true,
    backgroundPlaybackEnabled: true
  })

  const [playbackState, setPlaybackState] = useState<AudioPlaybackState>({
    isPlaying: false,
    isPaused: false,
    currentVerseNumber: 0,
    playbackRate: audioPreferences?.playbackRate || 1.0,
    volume: audioPreferences?.volume || 0.8,
    narratorId: audioPreferences?.defaultNarratorId || 'david-american',
    autoAdvanceChapter: audioPreferences?.autoAdvanceChapter || false
  })

  const [playlists] = useKV<AudioPlaylist[]>('audio-playlists', [])
  const [currentPlaylist, setCurrentPlaylist] = useState<AudioPlaylist | null>(null)

  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null)
  const currentVerseIndexRef = useRef<number>(0)
  const sleepTimerRef = useRef<NodeJS.Timeout | null>(null)
  const wakeLockRef = useRef<any>(null)

  const currentNarrator = narrators.find(n => n.id === playbackState.narratorId) || narrators[0]

  const speakVerse = useCallback((verseIndex: number) => {
    if (verseIndex >= verses.length) {
      setPlaybackState(prev => ({
        ...prev,
        isPlaying: false,
        isPaused: false,
        currentVerseNumber: 0
      }))
      return
    }

    const verse = verses[verseIndex]
    const utterance = new SpeechSynthesisUtterance(verse.text)
    
    if (currentNarrator?.voice) {
      utterance.voice = currentNarrator.voice
    }
    
    utterance.rate = playbackState.playbackRate
    utterance.volume = playbackState.volume
    utterance.lang = 'en-US'

    utterance.onstart = () => {
      setPlaybackState(prev => ({
        ...prev,
        currentVerseNumber: verse.verseNumber,
        isPlaying: true,
        isPaused: false
      }))
    }

    utterance.onend = () => {
      const nextIndex = verseIndex + 1
      if (nextIndex < verses.length && playbackState.isPlaying) {
        currentVerseIndexRef.current = nextIndex
        setTimeout(() => speakVerse(nextIndex), 500)
      } else {
        setPlaybackState(prev => ({
          ...prev,
          isPlaying: false,
          isPaused: false,
          currentVerseNumber: 0
        }))
      }
    }

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event)
      setPlaybackState(prev => ({
        ...prev,
        isPlaying: false,
        isPaused: false
      }))
    }

    utteranceRef.current = utterance
    window.speechSynthesis.speak(utterance)
  }, [verses, playbackState.playbackRate, playbackState.volume, playbackState.isPlaying, currentNarrator])

  const play = useCallback((startVerseNumber?: number) => {
    window.speechSynthesis.cancel()
    
    const startIndex = startVerseNumber 
      ? verses.findIndex(v => v.verseNumber === startVerseNumber)
      : currentVerseIndexRef.current

    currentVerseIndexRef.current = startIndex >= 0 ? startIndex : 0
    speakVerse(currentVerseIndexRef.current)
  }, [verses, speakVerse])

  const pause = useCallback(() => {
    window.speechSynthesis.pause()
    setPlaybackState(prev => ({
      ...prev,
      isPlaying: false,
      isPaused: true
    }))
  }, [])

  const resume = useCallback(() => {
    if (playbackState.isPaused) {
      window.speechSynthesis.resume()
      setPlaybackState(prev => ({
        ...prev,
        isPlaying: true,
        isPaused: false
      }))
    } else {
      play()
    }
  }, [playbackState.isPaused, play])

  const stop = useCallback(() => {
    window.speechSynthesis.cancel()
    currentVerseIndexRef.current = 0
    setPlaybackState(prev => ({
      ...prev,
      isPlaying: false,
      isPaused: false,
      currentVerseNumber: 0
    }))
  }, [])

  const skipToVerse = useCallback((verseNumber: number) => {
    const wasPlaying = playbackState.isPlaying
    stop()
    if (wasPlaying) {
      setTimeout(() => play(verseNumber), 100)
    } else {
      const verseIndex = verses.findIndex(v => v.verseNumber === verseNumber)
      currentVerseIndexRef.current = verseIndex >= 0 ? verseIndex : 0
      setPlaybackState(prev => ({
        ...prev,
        currentVerseNumber: verseNumber
      }))
    }
  }, [playbackState.isPlaying, stop, play, verses])

  const setNarrator = useCallback((narratorId: string) => {
    const wasPlaying = playbackState.isPlaying
    const currentVerse = playbackState.currentVerseNumber
    
    stop()
    
    setPlaybackState(prev => ({
      ...prev,
      narratorId
    }))
    
    setAudioPreferences(current => ({
      defaultNarratorId: narratorId,
      playbackRate: current?.playbackRate || 1.0,
      volume: current?.volume || 0.8,
      autoAdvanceChapter: current?.autoAdvanceChapter || false,
      highlightCurrentVerse: current?.highlightCurrentVerse || true,
      backgroundPlaybackEnabled: current?.backgroundPlaybackEnabled ?? true,
      sleepTimerDefault: current?.sleepTimerDefault
    }))

    if (wasPlaying && currentVerse > 0) {
      setTimeout(() => play(currentVerse), 100)
    }
  }, [playbackState.isPlaying, playbackState.currentVerseNumber, stop, play, setAudioPreferences])

  const setPlaybackRate = useCallback((rate: number) => {
    setPlaybackState(prev => ({
      ...prev,
      playbackRate: rate
    }))
    
    setAudioPreferences(current => ({
      defaultNarratorId: current?.defaultNarratorId || 'david-american',
      playbackRate: rate,
      volume: current?.volume || 0.8,
      autoAdvanceChapter: current?.autoAdvanceChapter || false,
      highlightCurrentVerse: current?.highlightCurrentVerse || true,
      backgroundPlaybackEnabled: current?.backgroundPlaybackEnabled ?? true,
      sleepTimerDefault: current?.sleepTimerDefault
    }))

    if (utteranceRef.current) {
      utteranceRef.current.rate = rate
    }
  }, [setAudioPreferences])

  const setVolume = useCallback((volume: number) => {
    setPlaybackState(prev => ({
      ...prev,
      volume
    }))
    
    setAudioPreferences(current => ({
      defaultNarratorId: current?.defaultNarratorId || 'david-american',
      playbackRate: current?.playbackRate || 1.0,
      volume: volume,
      autoAdvanceChapter: current?.autoAdvanceChapter || false,
      highlightCurrentVerse: current?.highlightCurrentVerse || true,
      backgroundPlaybackEnabled: current?.backgroundPlaybackEnabled ?? true,
      sleepTimerDefault: current?.sleepTimerDefault
    }))

    if (utteranceRef.current) {
      utteranceRef.current.volume = volume
    }
  }, [setAudioPreferences])

  const setSleepTimer = useCallback((minutes: number | null) => {
    if (sleepTimerRef.current) {
      clearTimeout(sleepTimerRef.current)
      sleepTimerRef.current = null
    }

    if (minutes === null || minutes === 0) {
      setPlaybackState(prev => ({
        ...prev,
        sleepTimerMinutes: undefined,
        sleepTimerEndTime: undefined
      }))
      return
    }

    const endTime = Date.now() + minutes * 60 * 1000
    setPlaybackState(prev => ({
      ...prev,
      sleepTimerMinutes: minutes,
      sleepTimerEndTime: endTime
    }))

    sleepTimerRef.current = setTimeout(() => {
      stop()
      setPlaybackState(prev => ({
        ...prev,
        sleepTimerMinutes: undefined,
        sleepTimerEndTime: undefined
      }))
    }, minutes * 60 * 1000)
  }, [stop])

  const requestWakeLock = useCallback(async () => {
    if ('wakeLock' in navigator && audioPreferences?.backgroundPlaybackEnabled) {
      try {
        wakeLockRef.current = await (navigator as any).wakeLock.request('screen')
      } catch (err) {
        console.log('Wake lock request failed:', err)
      }
    }
  }, [audioPreferences?.backgroundPlaybackEnabled])

  const releaseWakeLock = useCallback(() => {
    if (wakeLockRef.current) {
      wakeLockRef.current.release()
      wakeLockRef.current = null
    }
  }, [])

  useEffect(() => {
    if (playbackState.isPlaying) {
      requestWakeLock()
    } else {
      releaseWakeLock()
    }
  }, [playbackState.isPlaying, requestWakeLock, releaseWakeLock])

  const loadPlaylist = useCallback((playlist: AudioPlaylist) => {
    setCurrentPlaylist(playlist)
    setPlaybackState(prev => ({
      ...prev,
      currentPlaylistId: playlist.id,
      playlistPosition: 0
    }))
  }, [])

  const nextInPlaylist = useCallback(() => {
    if (!currentPlaylist || playbackState.playlistPosition === undefined) return null
    
    const nextPosition = playbackState.playlistPosition + 1
    if (nextPosition < currentPlaylist.items.length) {
      return currentPlaylist.items[nextPosition]
    }
    return null
  }, [currentPlaylist, playbackState.playlistPosition])

  const advancePlaylist = useCallback(() => {
    if (!currentPlaylist || playbackState.playlistPosition === undefined) return
    
    const nextPosition = playbackState.playlistPosition + 1
    if (nextPosition < currentPlaylist.items.length) {
      setPlaybackState(prev => ({
        ...prev,
        playlistPosition: nextPosition
      }))
      
      const nextItem = currentPlaylist.items[nextPosition]
      const event = new CustomEvent('playlist-advance', {
        detail: { bookId: nextItem.bookId, chapter: nextItem.chapter }
      })
      window.dispatchEvent(event)
    } else {
      stop()
      setCurrentPlaylist(null)
      setPlaybackState(prev => ({
        ...prev,
        currentPlaylistId: undefined,
        playlistPosition: undefined
      }))
    }
  }, [currentPlaylist, playbackState.playlistPosition, stop])

  useEffect(() => {
    return () => {
      window.speechSynthesis.cancel()
      if (sleepTimerRef.current) {
        clearTimeout(sleepTimerRef.current)
      }
      releaseWakeLock()
    }
  }, [releaseWakeLock])

  return {
    playbackState,
    currentNarrator,
    narrators,
    audioPreferences,
    playlists,
    currentPlaylist,
    play,
    pause,
    resume,
    stop,
    skipToVerse,
    setNarrator,
    setPlaybackRate,
    setVolume,
    setSleepTimer,
    loadPlaylist,
    nextInPlaylist,
    advancePlaylist
  }
}
