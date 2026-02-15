import { useEffect, useState } from 'react'
import { useKV } from '@github/spark/hooks'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Button } from '@/components/ui/button'
import { Bell, BellSlash, Plus, Trash, Check } from '@phosphor-icons/react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { toast } from 'sonner'

interface NotificationTime {
  id: string
  time: string
  enabled: boolean
  label?: string
}

interface VerseNotificationSettings {
  enabled: boolean
  times: NotificationTime[]
  soundEnabled: boolean
  showPreview: boolean
  lastNotificationSent?: number
}

export default function VerseOfDayNotifications() {
  const [settings, setSettings] = useKV<VerseNotificationSettings>('verse-notification-settings', {
    enabled: false,
    times: [],
    soundEnabled: true,
    showPreview: true
  })

  const [newTime, setNewTime] = useState('09:00')
  const [permissionStatus, setPermissionStatus] = useState<'granted' | 'denied' | 'default'>('default')

  useEffect(() => {
    if ('Notification' in window) {
      setPermissionStatus(Notification.permission)
    }
  }, [])

  useEffect(() => {
    if (!settings?.enabled || !settings?.times?.length) return

    const checkAndSendNotifications = () => {
      const now = new Date()
      const currentTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
      const today = now.toISOString().split('T')[0]
      const lastSent = settings.lastNotificationSent
      const lastSentDate = lastSent ? new Date(lastSent).toISOString().split('T')[0] : null

      settings.times.forEach(timeSlot => {
        if (timeSlot.enabled && timeSlot.time === currentTime) {
          if (lastSentDate !== today) {
            sendNotification(timeSlot)
            setSettings((current) => ({
              ...current!,
              lastNotificationSent: Date.now()
            }))
          }
        }
      })
    }

    const interval = setInterval(checkAndSendNotifications, 60000)
    checkAndSendNotifications()

    return () => clearInterval(interval)
  }, [settings?.enabled, settings?.times, settings?.lastNotificationSent])

  const requestNotificationPermission = async () => {
    if (!('Notification' in window)) {
      toast.error('Notifications are not supported in this browser')
      return false
    }

    if (Notification.permission === 'granted') {
      return true
    }

    if (Notification.permission === 'denied') {
      toast.error('Notification permission was denied. Please enable it in your browser settings.')
      return false
    }

    const permission = await Notification.requestPermission()
    setPermissionStatus(permission)

    if (permission === 'granted') {
      toast.success('Notifications enabled!')
      return true
    } else {
      toast.error('Notification permission denied')
      return false
    }
  }

  const sendNotification = (timeSlot: NotificationTime) => {
    if (!('Notification' in window) || Notification.permission !== 'granted') return

    const title = '📖 Verse of the Day'
    const body = settings?.showPreview 
      ? `Your daily verse is ready. Tap to read today's inspiring passage.`
      : 'Tap to read your verse of the day'

    const notification = new Notification(title, {
      body,
      icon: '/favicon.ico',
      badge: '/favicon.ico',
      tag: 'verse-of-day',
      requireInteraction: false,
      silent: !settings?.soundEnabled
    })

    notification.onclick = () => {
      window.focus()
      notification.close()
    }

    setTimeout(() => notification.close(), 10000)
  }

  const handleToggleNotifications = async (enabled: boolean) => {
    if (enabled) {
      const hasPermission = await requestNotificationPermission()
      if (!hasPermission) return
    }

    setSettings((current) => ({
      ...current!,
      enabled
    }))

    toast.success(enabled ? 'Notifications enabled' : 'Notifications disabled')
  }

  const handleAddTime = () => {
    if (!newTime) return

    const existingTime = settings?.times?.find(t => t.time === newTime)
    if (existingTime) {
      toast.error('This time is already added')
      return
    }

    const timeSlot: NotificationTime = {
      id: `time-${Date.now()}`,
      time: newTime,
      enabled: true,
      label: formatTimeLabel(newTime)
    }

    setSettings((current) => ({
      ...current!,
      times: [...(current?.times || []), timeSlot]
    }))

    toast.success(`Notification time added: ${formatTimeLabel(newTime)}`)
  }

  const handleRemoveTime = (id: string) => {
    setSettings((current) => ({
      ...current!,
      times: current!.times.filter(t => t.id !== id)
    }))
    toast.success('Notification time removed')
  }

  const handleToggleTime = (id: string) => {
    setSettings((current) => ({
      ...current!,
      times: current!.times.map(t => 
        t.id === id ? { ...t, enabled: !t.enabled } : t
      )
    }))
  }

  const handleTestNotification = async () => {
    if (Notification.permission !== 'granted') {
      const hasPermission = await requestNotificationPermission()
      if (!hasPermission) return
    }

    sendNotification({
      id: 'test',
      time: '',
      enabled: true,
      label: 'Test'
    })

    toast.success('Test notification sent')
  }

  const formatTimeLabel = (time: string) => {
    const [hours, minutes] = time.split(':').map(Number)
    const period = hours >= 12 ? 'PM' : 'AM'
    const displayHours = hours % 12 || 12
    return `${displayHours}:${String(minutes).padStart(2, '0')} ${period}`
  }

  const generateTimeOptions = (): string[] => {
    const options: string[] = []
    for (let hour = 0; hour < 24; hour++) {
      for (let minute = 0; minute < 60; minute += 30) {
        const time = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
        options.push(time)
      }
    }
    return options
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bell size={24} weight="duotone" className="text-primary" />
          Verse of the Day Notifications
        </CardTitle>
        <CardDescription>
          Receive daily reminders to read your verse of the day
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <Label className="font-medium">Enable Notifications</Label>
            <p className="text-sm text-muted-foreground">
              Get notified at your chosen times each day
            </p>
          </div>
          <Switch
            checked={settings?.enabled || false}
            onCheckedChange={handleToggleNotifications}
          />
        </div>

        {permissionStatus === 'denied' && (
          <div className="p-3 rounded-md bg-destructive/10 border border-destructive/20">
            <div className="flex items-start gap-2">
              <BellSlash size={20} className="text-destructive mt-0.5" />
              <div className="flex-1 text-sm">
                <p className="font-medium text-destructive mb-1">Notifications Blocked</p>
                <p className="text-muted-foreground">
                  Please enable notifications in your browser settings to receive verse reminders.
                </p>
              </div>
            </div>
          </div>
        )}

        {permissionStatus === 'default' && settings?.enabled && (
          <div className="p-3 rounded-md bg-accent/10 border border-accent/20">
            <div className="flex items-start gap-2">
              <Bell size={20} className="text-accent mt-0.5" />
              <div className="flex-1 text-sm">
                <p className="font-medium text-accent mb-1">Permission Needed</p>
                <p className="text-muted-foreground mb-2">
                  Click the button below to allow notifications.
                </p>
                <Button 
                  size="sm" 
                  onClick={requestNotificationPermission}
                  className="gap-2"
                >
                  <Bell size={16} />
                  Enable Notifications
                </Button>
              </div>
            </div>
          </div>
        )}

        <Separator />

        <div className="space-y-3">
          <Label className="font-medium">Notification Times</Label>
          <p className="text-sm text-muted-foreground">
            Add one or more times to receive your daily verse reminder
          </p>

          {settings?.times && settings.times.length > 0 && (
            <div className="space-y-2">
              {settings.times.map(timeSlot => (
                <div 
                  key={timeSlot.id}
                  className="flex items-center justify-between p-3 rounded-md border bg-card hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <Switch
                      checked={timeSlot.enabled}
                      onCheckedChange={() => handleToggleTime(timeSlot.id)}
                      disabled={!settings?.enabled}
                    />
                    <div>
                      <p className="font-medium">{timeSlot.label || formatTimeLabel(timeSlot.time)}</p>
                      <p className="text-xs text-muted-foreground">
                        {timeSlot.enabled ? 'Active' : 'Disabled'}
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleRemoveTime(timeSlot.id)}
                  >
                    <Trash size={18} className="text-destructive" />
                  </Button>
                </div>
              ))}
            </div>
          )}

          <div className="flex gap-2">
            <Select value={newTime} onValueChange={setNewTime}>
              <SelectTrigger className="flex-1">
                <SelectValue placeholder="Select time" />
              </SelectTrigger>
              <SelectContent className="max-h-60">
                {generateTimeOptions().map(time => (
                  <SelectItem key={time} value={time}>
                    {formatTimeLabel(time)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button onClick={handleAddTime} className="gap-2">
              <Plus size={18} weight="bold" />
              Add
            </Button>
          </div>

          {(!settings?.times || settings.times.length === 0) && (
            <div className="text-center py-6 text-muted-foreground">
              <Bell size={40} weight="duotone" className="mx-auto mb-2 opacity-50" />
              <p className="text-sm">No notification times set</p>
              <p className="text-xs">Add a time to receive daily reminders</p>
            </div>
          )}
        </div>

        <Separator />

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="font-medium">Notification Sound</Label>
              <p className="text-sm text-muted-foreground">
                Play sound with notifications
              </p>
            </div>
            <Switch
              checked={settings?.soundEnabled || false}
              onCheckedChange={(checked) => 
                setSettings((current) => ({
                  ...current!,
                  soundEnabled: checked
                }))
              }
              disabled={!settings?.enabled}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="font-medium">Show Preview</Label>
              <p className="text-sm text-muted-foreground">
                Include description in notification
              </p>
            </div>
            <Switch
              checked={settings?.showPreview ?? true}
              onCheckedChange={(checked) => 
                setSettings((current) => ({
                  ...current!,
                  showPreview: checked
                }))
              }
              disabled={!settings?.enabled}
            />
          </div>
        </div>

        <Separator />

        <div className="space-y-3">
          <Button
            variant="outline"
            onClick={handleTestNotification}
            className="w-full gap-2"
            disabled={permissionStatus !== 'granted'}
          >
            <Bell size={18} />
            Send Test Notification
          </Button>

          {settings?.lastNotificationSent && (
            <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
              <Check size={14} />
              Last notification: {new Date(settings.lastNotificationSent).toLocaleString()}
            </div>
          )}
        </div>

        <div className="p-3 rounded-md bg-muted/30 text-xs text-muted-foreground space-y-1">
          <p>
            <strong>Note:</strong> Notifications work best when the app is open or in the background.
            Some browsers may limit notifications when the tab is closed.
          </p>
          <p className="pt-1">
            Your notification preferences are saved locally and will persist across sessions.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
