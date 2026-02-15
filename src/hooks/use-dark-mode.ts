import { useEffect } from 'react'
import { useKV } from '@github/spark/hooks'
import type { UserProfile } from '@/lib/types'

export function useDarkMode() {
  const [userProfile] = useKV<UserProfile>('user-profile', {
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

  const isDarkMode = userProfile?.preferences.nightMode || false

  useEffect(() => {
    const root = document.documentElement
    if (isDarkMode) {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
  }, [isDarkMode])

  return isDarkMode
}
