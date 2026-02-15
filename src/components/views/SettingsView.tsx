import { useState } from 'react'
import { useKV } from '@github/spark/hooks'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Gear, TextAa, Moon, DownloadSimple, Users, ShieldCheck, Bell, Keyboard, MapPin, SunHorizon, Clock } from '@phosphor-icons/react'
import { translations } from '@/lib/data'
import type { UserProfile } from '@/lib/types'
import CommunityProfileSettings from '@/components/social/CommunityProfileSettings'
import ModeratorTestPanel from '@/components/social/ModeratorTestPanel'
import VerseOfDayNotifications from './VerseOfDayNotifications'
import KeyboardShortcutsDialog from '@/components/KeyboardShortcutsDialog'
import { useAutoDarkMode, formatSunTime, type DarkModeSchedule } from '@/hooks/use-auto-dark-mode'

interface SettingsViewProps {
  userProfile: UserProfile
}

export default function SettingsView({ userProfile: initialProfile }: SettingsViewProps) {
  const [userProfile, setUserProfile] = useKV<UserProfile>('user-profile', initialProfile)
  const [showKeyboardShortcuts, setShowKeyboardShortcuts] = useState(false)
  const { settings: darkModeSettings, updateSettings: updateDarkModeSettings } = useAutoDarkMode()

  const updatePreference = <K extends keyof UserProfile['preferences']>(
    key: K,
    value: UserProfile['preferences'][K]
  ) => {
    setUserProfile(current => ({
      ...current!,
      preferences: {
        ...current!.preferences,
        [key]: value
      }
    }))
  }

  const handleDarkModeScheduleChange = (mode: DarkModeSchedule) => {
    updateDarkModeSettings(current => ({
      ...current!,
      mode
    }))
  }

  const handleScheduledTimeChange = (type: 'start' | 'end', value: string) => {
    updateDarkModeSettings(current => ({
      ...current!,
      [type === 'start' ? 'scheduledStart' : 'scheduledEnd']: value
    }))
  }

  const sunriseTime = formatSunTime(darkModeSettings || { mode: 'manual' }, 'sunrise')
  const sunsetTime = formatSunTime(darkModeSettings || { mode: 'manual' }, 'sunset')

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2 text-foreground flex items-center gap-3" style={{ fontFamily: 'var(--font-heading)' }}>
          <Gear size={32} weight="duotone" className="text-primary" />
          Settings
        </h2>
        <p className="text-muted-foreground">
          Customize your Bible study experience
        </p>
      </div>

      <Tabs defaultValue="reading" className="space-y-6">
        <TabsList>
          <TabsTrigger value="reading" className="gap-2">
            <TextAa size={16} weight="duotone" />
            Reading
          </TabsTrigger>
          <TabsTrigger value="notifications" className="gap-2">
            <Bell size={16} weight="duotone" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="accessibility" className="gap-2">
            <Keyboard size={16} weight="duotone" />
            Accessibility
          </TabsTrigger>
          <TabsTrigger value="community" className="gap-2">
            <Users size={16} weight="duotone" />
            Community
          </TabsTrigger>
          <TabsTrigger value="permissions" className="gap-2">
            <ShieldCheck size={16} weight="duotone" />
            Permissions
          </TabsTrigger>
        </TabsList>

        <TabsContent value="reading" className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TextAa size={24} weight="duotone" className="text-primary" />
              Reading Preferences
            </CardTitle>
            <CardDescription>
              Adjust how scripture text appears
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label>Font Size: {userProfile?.preferences.fontSize}px</Label>
              <Slider
                value={[userProfile?.preferences.fontSize || 18]}
                onValueChange={(value) => updatePreference('fontSize', value[0])}
                min={12}
                max={28}
                step={1}
                className="w-full"
              />
              <p className="text-sm text-muted-foreground">
                Adjust text size for comfortable reading
              </p>
            </div>

            <Separator />

            <div className="space-y-2">
              <Label>Line Spacing: {userProfile?.preferences.lineSpacing}</Label>
              <Slider
                value={[userProfile?.preferences.lineSpacing || 1.75]}
                onValueChange={(value) => updatePreference('lineSpacing', value[0])}
                min={1.2}
                max={2.5}
                step={0.05}
                className="w-full"
              />
              <p className="text-sm text-muted-foreground">
                Adjust spacing between lines of text
              </p>
            </div>

            <Separator />

            <div className="space-y-2">
              <Label>Font Family</Label>
              <Select
                value={userProfile?.preferences.fontFamily}
                onValueChange={(value) => updatePreference('fontFamily', value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Literata">Literata (Default)</SelectItem>
                  <SelectItem value="Crimson Pro">Crimson Pro</SelectItem>
                  <SelectItem value="Georgia">Georgia</SelectItem>
                  <SelectItem value="Times New Roman">Times New Roman</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-sm text-muted-foreground">
                Choose your preferred reading font
              </p>
            </div>

            <Separator />

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Verse Numbers</Label>
                <p className="text-sm text-muted-foreground">
                  Show verse numbers in text
                </p>
              </div>
              <Switch
                checked={userProfile?.preferences.verseNumbersVisible}
                onCheckedChange={(checked) => updatePreference('verseNumbersVisible', checked)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Red Letter Text</Label>
                <p className="text-sm text-muted-foreground">
                  Highlight Jesus' words in red
                </p>
              </div>
              <Switch
                checked={userProfile?.preferences.redLetterText}
                onCheckedChange={(checked) => updatePreference('redLetterText', checked)}
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Moon size={24} weight="duotone" className="text-primary" />
              Dark Mode & Scheduling
            </CardTitle>
            <CardDescription>
              Configure automatic dark mode based on time or location
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Dark Mode Schedule</Label>
                <Select
                  value={darkModeSettings?.mode || 'manual'}
                  onValueChange={handleDarkModeScheduleChange}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="manual">
                      <div className="flex items-center gap-2">
                        <Moon size={16} weight="duotone" />
                        <span>Manual - Toggle manually</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="auto">
                      <div className="flex items-center gap-2">
                        <SunHorizon size={16} weight="duotone" />
                        <span>Automatic - Sunset to sunrise</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="scheduled">
                      <div className="flex items-center gap-2">
                        <Clock size={16} weight="duotone" />
                        <span>Scheduled - Custom times</span>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-sm text-muted-foreground">
                  Choose how dark mode should be activated
                </p>
              </div>

              {darkModeSettings?.mode === 'manual' && (
                <div className="p-4 bg-muted/50 rounded-md space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Dark Mode</Label>
                      <p className="text-sm text-muted-foreground">
                        Manually toggle dark theme on/off
                      </p>
                    </div>
                    <Switch
                      checked={userProfile?.preferences.nightMode}
                      onCheckedChange={(checked) => updatePreference('nightMode', checked)}
                    />
                  </div>
                </div>
              )}

              {darkModeSettings?.mode === 'auto' && (
                <div className="p-4 bg-muted/50 rounded-md space-y-3">
                  <div className="flex items-center gap-2 text-sm">
                    <MapPin size={16} weight="duotone" className="text-primary" />
                    <span className="font-medium">Location-Based Scheduling</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Dark mode will automatically activate at sunset and deactivate at sunrise based on your location.
                  </p>
                  {darkModeSettings.latitude && darkModeSettings.longitude && (
                    <div className="space-y-2 pt-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Today's sunrise:</span>
                        <Badge variant="secondary" className="gap-1">
                          <SunHorizon size={14} weight="duotone" />
                          {sunriseTime || 'Calculating...'}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Today's sunset:</span>
                        <Badge variant="secondary" className="gap-1">
                          <SunHorizon size={14} weight="duotone" />
                          {sunsetTime || 'Calculating...'}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground pt-2">
                        Location: {darkModeSettings.latitude.toFixed(4)}°, {darkModeSettings.longitude.toFixed(4)}°
                      </p>
                    </div>
                  )}
                  {(!darkModeSettings.latitude || !darkModeSettings.longitude) && (
                    <div className="flex items-center gap-2 text-xs text-muted-foreground pt-2">
                      <MapPin size={14} weight="duotone" />
                      <span>Requesting location permission...</span>
                    </div>
                  )}
                </div>
              )}

              {darkModeSettings?.mode === 'scheduled' && (
                <div className="p-4 bg-muted/50 rounded-md space-y-4">
                  <div className="flex items-center gap-2 text-sm">
                    <Clock size={16} weight="duotone" className="text-primary" />
                    <span className="font-medium">Custom Time Schedule</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Set specific times when dark mode should be active each day.
                  </p>
                  <div className="grid grid-cols-2 gap-4 pt-2">
                    <div className="space-y-2">
                      <Label htmlFor="dark-mode-start">Start Time</Label>
                      <Input
                        id="dark-mode-start"
                        type="time"
                        value={darkModeSettings.scheduledStart || '20:00'}
                        onChange={(e) => handleScheduledTimeChange('start', e.target.value)}
                        className="font-mono"
                      />
                      <p className="text-xs text-muted-foreground">
                        Dark mode begins
                      </p>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="dark-mode-end">End Time</Label>
                      <Input
                        id="dark-mode-end"
                        type="time"
                        value={darkModeSettings.scheduledEnd || '07:00'}
                        onChange={(e) => handleScheduledTimeChange('end', e.target.value)}
                        className="font-mono"
                      />
                      <p className="text-xs text-muted-foreground">
                        Dark mode ends
                      </p>
                    </div>
                  </div>
                  <div className="pt-2">
                    <Badge variant="outline" className="gap-1">
                      <Clock size={14} weight="duotone" />
                      Active from {darkModeSettings.scheduledStart || '20:00'} to {darkModeSettings.scheduledEnd || '07:00'}
                    </Badge>
                  </div>
                </div>
              )}

              <Separator />

              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Badge variant={userProfile?.preferences.nightMode ? 'default' : 'secondary'}>
                    {userProfile?.preferences.nightMode ? 'Dark mode active' : 'Light mode active'}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">
                  Current theme status • Changes apply immediately across the entire app
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Translation Preferences</CardTitle>
            <CardDescription>
              Choose your default translation and comparison set
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label>Default Translation</Label>
              <Select
                value={userProfile?.preferences.defaultTranslation}
                onValueChange={(value) => updatePreference('defaultTranslation', value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {translations.map(trans => (
                    <SelectItem key={trans.id} value={trans.id}>
                      {trans.name} ({trans.shortCode})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <p className="text-sm text-muted-foreground">
                Primary translation for reading
              </p>
            </div>

            <Separator />

            <div className="space-y-2">
              <Label>Comparison Set</Label>
              <p className="text-sm text-muted-foreground mb-3">
                Translations to show in comparison view
              </p>
              <div className="flex flex-wrap gap-2">
                {translations.map(trans => {
                  const isSelected = userProfile?.preferences.comparisonSet.includes(trans.id)
                  return (
                    <Badge
                      key={trans.id}
                      variant={isSelected ? 'default' : 'outline'}
                      className="cursor-pointer transition-all hover:scale-105"
                      onClick={() => {
                        const current = userProfile?.preferences.comparisonSet || []
                        if (isSelected) {
                          updatePreference('comparisonSet', current.filter(id => id !== trans.id))
                        } else {
                          updatePreference('comparisonSet', [...current, trans.id])
                        }
                      }}
                    >
                      {trans.shortCode}
                    </Badge>
                  )
                })}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DownloadSimple size={24} weight="duotone" className="text-primary" />
              Offline Downloads
            </CardTitle>
            <CardDescription>
              Download translations for offline reading
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {translations.map(trans => (
                <div key={trans.id} className="flex items-center justify-between p-3 rounded-md bg-muted/50">
                  <div>
                    <p className="font-medium">{trans.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {trans.year} • {trans.licenseRestrictions.offlineAllowed ? 'Offline available' : 'Streaming only'}
                    </p>
                  </div>
                  <Badge variant={trans.licenseRestrictions.offlineAllowed ? 'default' : 'secondary'}>
                    {trans.licenseRestrictions.offlineAllowed ? 'Downloaded' : 'Limited'}
                  </Badge>
                </div>
              ))}
            </div>
            <p className="text-xs text-muted-foreground mt-4">
              Some translations have license restrictions that limit offline availability or excerpt length.
            </p>
          </CardContent>
        </Card>

        <Card className="bg-muted/30">
          <CardHeader>
            <CardTitle className="text-lg">About</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground space-y-2">
            <p>
              <strong>Geneva Bible Study</strong> - A scholarly platform for studying the Bible with historical context
            </p>
            <p>
              Version 1.0.0 • Built with reverence for ancient texts and modern scholarship
            </p>
            <Separator className="my-3" />
            <p className="text-xs">
              All translations and texts are used according to their respective licenses and copyrights.
              See individual translation information for specific terms and restrictions.
            </p>
          </CardContent>
        </Card>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-6">
          <VerseOfDayNotifications />
        </TabsContent>

        <TabsContent value="accessibility" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Keyboard size={24} weight="duotone" className="text-primary" />
                Accessibility Features
              </CardTitle>
              <CardDescription>
                Features to help make the app more accessible
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="p-4 bg-muted/50 rounded-md">
                  <h4 className="font-semibold mb-2">Voice-to-Text Messaging</h4>
                  <p className="text-sm text-muted-foreground mb-3">
                    Record voice messages in conversations and group chats. The app will automatically transcribe your audio to text, which you can review and edit before sending.
                  </p>
                  <Badge variant="default">Active</Badge>
                </div>

                <Separator />

                <div className="p-4 bg-muted/50 rounded-md">
                  <h4 className="font-semibold mb-2">Editable Transcriptions</h4>
                  <p className="text-sm text-muted-foreground mb-3">
                    All AI-generated transcriptions (voice annotations, voice messages) can be edited for accuracy. Original transcriptions are preserved for reference.
                  </p>
                  <Badge variant="default">Active</Badge>
                </div>

                <Separator />

                <div className="p-4 bg-muted/50 rounded-md">
                  <h4 className="font-semibold mb-2 flex items-center justify-between">
                    <span>Keyboard Shortcuts</span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowKeyboardShortcuts(true)}
                      className="gap-2"
                    >
                      <Keyboard size={16} />
                      View Shortcuts
                    </Button>
                  </h4>
                  <p className="text-sm text-muted-foreground mb-3">
                    Navigate the app efficiently using keyboard shortcuts. Press Ctrl+/ (⌘+/ on Mac) anytime to view all shortcuts.
                  </p>
                  <div className="flex gap-2 flex-wrap mt-2">
                    <Badge variant="secondary">Ctrl+K - Search</Badge>
                    <Badge variant="secondary">1-9 - Switch Tabs</Badge>
                    <Badge variant="secondary">Space - Play/Pause</Badge>
                    <Badge variant="secondary">Escape - Go Back</Badge>
                  </div>
                </div>

                <Separator />

                <div className="p-4 bg-muted/50 rounded-md">
                  <h4 className="font-semibold mb-2">Screen Reader Support</h4>
                  <p className="text-sm text-muted-foreground mb-3">
                    All interactive elements include proper ARIA labels and semantic HTML for screen reader compatibility.
                  </p>
                  <Badge variant="default">Active</Badge>
                </div>

                <Separator />

                <div className="p-4 bg-muted/50 rounded-md">
                  <h4 className="font-semibold mb-2">High Contrast Mode</h4>
                  <p className="text-sm text-muted-foreground mb-3">
                    The app respects your system's high contrast settings and maintains WCAG AA contrast ratios (4.5:1) throughout the interface.
                  </p>
                  <Badge variant="default">Active</Badge>
                </div>

                <Separator />

                <div className="p-4 bg-muted/50 rounded-md">
                  <h4 className="font-semibold mb-2">Adjustable Typography</h4>
                  <p className="text-sm text-muted-foreground mb-3">
                    Customize font size (12-28px) and line spacing (1.0-2.5) in the Reading settings tab for comfortable long-form reading.
                  </p>
                  <Badge variant="default">Active</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="community">
          <CommunityProfileSettings />
        </TabsContent>

        <TabsContent value="permissions" className="space-y-6">
          <ModeratorTestPanel />
        </TabsContent>
      </Tabs>

      <KeyboardShortcutsDialog
        open={showKeyboardShortcuts}
        onOpenChange={setShowKeyboardShortcuts}
      />
    </div>
  )
}