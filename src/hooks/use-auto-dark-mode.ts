import { useEffect } from 'react'
import { useKV } from '@github/spark/hooks'
import type { UserProfile } from '@/lib/types'

export type DarkModeSchedule = 'manual' | 'auto' | 'scheduled'

export interface DarkModeSettings {
  mode: DarkModeSchedule
  scheduledStart?: string
  scheduledEnd?: string
  latitude?: number
  longitude?: number
  lastSunsetCalculation?: number
}

interface SunTimes {
  sunrise: Date
  sunset: Date
}

function calculateSunTimes(lat: number, lng: number, date: Date = new Date()): SunTimes {
  const J2000 = 2451545.0
  const julianDate = date.getTime() / 86400000 + 2440587.5
  const n = julianDate - J2000
  
  const lngHour = lng / 15
  
  const t = n + ((6 - lngHour) / 24)
  const tSunset = n + ((18 - lngHour) / 24)
  
  const M = (0.9856 * t) - 3.289
  const MSunset = (0.9856 * tSunset) - 3.289
  
  let L = M + (1.916 * Math.sin(M * Math.PI / 180)) + (0.020 * Math.sin(2 * M * Math.PI / 180)) + 282.634
  let LSunset = MSunset + (1.916 * Math.sin(MSunset * Math.PI / 180)) + (0.020 * Math.sin(2 * MSunset * Math.PI / 180)) + 282.634
  
  L = L % 360
  LSunset = LSunset % 360
  
  let RA = Math.atan(0.91764 * Math.tan(L * Math.PI / 180)) * 180 / Math.PI
  let RASunset = Math.atan(0.91764 * Math.tan(LSunset * Math.PI / 180)) * 180 / Math.PI
  
  RA = RA % 360
  RASunset = RASunset % 360
  
  const Lquadrant = Math.floor(L / 90) * 90
  const RAquadrant = Math.floor(RA / 90) * 90
  RA = RA + (Lquadrant - RAquadrant)
  
  const LquadrantSunset = Math.floor(LSunset / 90) * 90
  const RAquadrantSunset = Math.floor(RASunset / 90) * 90
  RASunset = RASunset + (LquadrantSunset - RAquadrantSunset)
  
  RA = RA / 15
  RASunset = RASunset / 15
  
  const sinDec = 0.39782 * Math.sin(L * Math.PI / 180)
  const cosDec = Math.cos(Math.asin(sinDec))
  
  const sinDecSunset = 0.39782 * Math.sin(LSunset * Math.PI / 180)
  const cosDecSunset = Math.cos(Math.asin(sinDecSunset))
  
  const zenith = 90.833
  const cosH = (Math.cos(zenith * Math.PI / 180) - (sinDec * Math.sin(lat * Math.PI / 180))) / (cosDec * Math.cos(lat * Math.PI / 180))
  const cosHSunset = (Math.cos(zenith * Math.PI / 180) - (sinDecSunset * Math.sin(lat * Math.PI / 180))) / (cosDecSunset * Math.cos(lat * Math.PI / 180))
  
  if (cosH > 1 || cosH < -1 || cosHSunset > 1 || cosHSunset < -1) {
    const midnightSun = lat > 0 ? date.getMonth() >= 3 && date.getMonth() <= 8 : date.getMonth() < 3 || date.getMonth() > 8
    
    if (midnightSun) {
      const sunrise = new Date(date)
      sunrise.setHours(0, 0, 0, 0)
      const sunset = new Date(date)
      sunset.setHours(23, 59, 59, 999)
      return { sunrise, sunset }
    } else {
      const sunrise = new Date(date)
      sunrise.setHours(12, 0, 0, 0)
      const sunset = new Date(date)
      sunset.setHours(12, 0, 0, 0)
      return { sunrise, sunset }
    }
  }
  
  const H = 360 - (Math.acos(cosH) * 180 / Math.PI)
  const HSunset = Math.acos(cosHSunset) * 180 / Math.PI
  
  const T = H / 15 + RA - (0.06571 * t) - 6.622
  const TSunset = HSunset / 15 + RASunset - (0.06571 * tSunset) - 6.622
  
  let UT = T - lngHour
  let UTSunset = TSunset - lngHour
  
  UT = UT % 24
  UTSunset = UTSunset % 24
  
  if (UT < 0) UT += 24
  if (UTSunset < 0) UTSunset += 24
  
  const sunriseHours = Math.floor(UT)
  const sunriseMinutes = Math.round((UT - sunriseHours) * 60)
  
  const sunsetHours = Math.floor(UTSunset)
  const sunsetMinutes = Math.round((UTSunset - sunsetHours) * 60)
  
  const sunrise = new Date(date)
  sunrise.setUTCHours(sunriseHours, sunriseMinutes, 0, 0)
  
  const sunset = new Date(date)
  sunset.setUTCHours(sunsetHours, sunsetMinutes, 0, 0)
  
  return { sunrise, sunset }
}

function getLocation(): Promise<{ latitude: number; longitude: number }> {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation is not supported'))
      return
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        })
      },
      (error) => {
        reject(error)
      },
      {
        timeout: 10000,
        maximumAge: 3600000
      }
    )
  })
}

function shouldBeDarkMode(settings: DarkModeSettings): boolean {
  const now = new Date()
  
  if (settings.mode === 'auto') {
    if (!settings.latitude || !settings.longitude) {
      return false
    }
    
    const { sunrise, sunset } = calculateSunTimes(settings.latitude, settings.longitude, now)
    
    return now < sunrise || now >= sunset
  }
  
  if (settings.mode === 'scheduled') {
    if (!settings.scheduledStart || !settings.scheduledEnd) {
      return false
    }
    
    const [startHour, startMin] = settings.scheduledStart.split(':').map(Number)
    const [endHour, endMin] = settings.scheduledEnd.split(':').map(Number)
    
    const currentMinutes = now.getHours() * 60 + now.getMinutes()
    const startMinutes = startHour * 60 + startMin
    const endMinutes = endHour * 60 + endMin
    
    if (startMinutes < endMinutes) {
      return currentMinutes >= startMinutes && currentMinutes < endMinutes
    } else {
      return currentMinutes >= startMinutes || currentMinutes < endMinutes
    }
  }
  
  return false
}

export function useAutoDarkMode() {
  const [darkModeSettings, setDarkModeSettings] = useKV<DarkModeSettings>('dark-mode-settings', {
    mode: 'manual'
  })

  const [userProfile, setUserProfile] = useKV<UserProfile>('user-profile', {
    id: 'default-user',
    displayName: 'Reader',
    role: 'reader',
    preferences: {
      defaultTranslation: 'geneva',
      comparisonSet: ['geneva', 'kjv', 'esv', 'niv'],
      fontSize: 18,
      lineSpacing: 1.75,
      fontFamily: 'Literata',
      nightMode: false,
      redLetterText: false,
      verseNumbersVisible: true
    }
  })

  useEffect(() => {
    if (!darkModeSettings) return

    async function updateLocation() {
      if (darkModeSettings?.mode === 'auto') {
        const now = Date.now()
        const lastCalculation = darkModeSettings.lastSunsetCalculation || 0
        const twentyFourHours = 24 * 60 * 60 * 1000
        
        if (!darkModeSettings.latitude || !darkModeSettings.longitude || (now - lastCalculation) > twentyFourHours) {
          try {
            const location = await getLocation()
            setDarkModeSettings((current) => ({
              ...current!,
              latitude: location.latitude,
              longitude: location.longitude,
              lastSunsetCalculation: now
            }))
          } catch (error) {
            console.warn('Could not get location for auto dark mode:', error)
          }
        }
      }
    }

    updateLocation()

    const checkInterval = setInterval(() => {
      if (darkModeSettings.mode === 'auto' || darkModeSettings.mode === 'scheduled') {
        const shouldBeDark = shouldBeDarkMode(darkModeSettings)
        const currentlyDark = userProfile?.preferences?.nightMode || false
        
        if (shouldBeDark !== currentlyDark) {
          setUserProfile((current) => ({
            ...current!,
            preferences: {
              ...current!.preferences,
              nightMode: shouldBeDark
            }
          }))
        }
      }
    }, 60000)

    if (darkModeSettings.mode === 'auto' || darkModeSettings.mode === 'scheduled') {
      const shouldBeDark = shouldBeDarkMode(darkModeSettings)
      const currentlyDark = userProfile?.preferences?.nightMode || false
      
      if (shouldBeDark !== currentlyDark) {
        setUserProfile((current) => ({
          ...current!,
          preferences: {
            ...current!.preferences,
            nightMode: shouldBeDark
          }
        }))
      }
    }

    return () => clearInterval(checkInterval)
  }, [darkModeSettings?.mode, darkModeSettings?.scheduledStart, darkModeSettings?.scheduledEnd, darkModeSettings?.latitude, darkModeSettings?.longitude])

  return {
    settings: darkModeSettings,
    updateSettings: setDarkModeSettings
  }
}

export function formatSunTime(settings: DarkModeSettings, type: 'sunrise' | 'sunset'): string | null {
  if (!settings.latitude || !settings.longitude) return null
  
  try {
    const { sunrise, sunset } = calculateSunTimes(settings.latitude, settings.longitude)
    const time = type === 'sunrise' ? sunrise : sunset
    
    return time.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    })
  } catch {
    return null
  }
}
