import { useState, useEffect } from 'react'
import { useKV } from '@github/spark/hooks'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Bell, BellSlash, Check } from '@phosphor-icons/react'
import type { NotificationSettings } from '@/lib/types'
import { toast } from 'sonner'

interface NotificationSettingsProps {
  planId?: string
}

export default function NotificationSettingsPanel({ planId }: NotificationSettingsProps) {
  const [settings = {
    enabled: false,
    dailyReminderTime: '08:00',
    soundEnabled: true,
    desktopNotifications: false,
    missedDayReminders: true
  }, setSettings] = useKV<NotificationSettings>('notification-settings', {
    enabled: false,
    dailyReminderTime: '08:00',
    soundEnabled: true,
    desktopNotifications: false,
    missedDayReminders: true
  })

  const [hasPermission, setHasPermission] = useState(false)

  useEffect(() => {
    if ('Notification' in window) {
      setHasPermission(Notification.permission === 'granted')
    }
  }, [])

  const requestNotificationPermission = async () => {
    if (!('Notification' in window)) {
      toast.error('Notifications not supported in this browser')
      return
    }

    try {
      const permission = await Notification.requestPermission()
      setHasPermission(permission === 'granted')
      
      if (permission === 'granted') {
        toast.success('Notification permissions granted!')
        setSettings(current => ({ 
          ...current!, 
          desktopNotifications: true 
        }))
      } else {
        toast.error('Notification permissions denied')
      }
    } catch (error) {
      toast.error('Error requesting notification permissions')
    }
  }

  const sendTestNotification = () => {
    if (!hasPermission) {
      toast.error('Please enable notification permissions first')
      return
    }

    new Notification('Geneva Bible Study', {
      body: "Time for today's reading! 📖",
      icon: '/icon.png',
      badge: '/badge.png'
    })

    toast.success('Test notification sent!')
  }

  const scheduleReminder = () => {
    if (!settings.enabled || !settings.dailyReminderTime) {
      return
    }

    const [hours, minutes] = settings.dailyReminderTime.split(':').map(Number)
    const now = new Date()
    const scheduledTime = new Date(now.getFullYear(), now.getMonth(), now.getDate(), hours, minutes)

    if (scheduledTime < now) {
      scheduledTime.setDate(scheduledTime.getDate() + 1)
    }

    const timeUntilReminder = scheduledTime.getTime() - now.getTime()

    setTimeout(() => {
      if (settings.desktopNotifications && hasPermission) {
        new Notification('Geneva Bible Study', {
          body: "Time for today's reading! 📖",
          icon: '/icon.png'
        })
      }

      toast('Time for your daily reading!', {
        icon: '📖',
        duration: 10000
      })

      scheduleReminder()
    }, timeUntilReminder)

    toast.success(`Reminder set for ${settings.dailyReminderTime}`)
  }

  useEffect(() => {
    if (settings.enabled) {
      scheduleReminder()
    }
  }, [settings.enabled, settings.dailyReminderTime])

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-3">
          {settings.enabled ? (
            <Bell size={24} weight="duotone" className="text-accent" />
          ) : (
            <BellSlash size={24} weight="duotone" className="text-muted-foreground" />
          )}
          <div>
            <CardTitle>Reading Reminders</CardTitle>
            <CardDescription>Get notified when it's time to read</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <Label htmlFor="enable-reminders">Enable Daily Reminders</Label>
            <p className="text-sm text-muted-foreground">
              Receive a reminder at your preferred time each day
            </p>
          </div>
          <Switch
            id="enable-reminders"
            checked={settings.enabled}
            onCheckedChange={(checked) => 
              setSettings(current => ({ ...current!, enabled: checked }))
            }
          />
        </div>

        {settings.enabled && (
          <>
            <div className="space-y-2">
              <Label htmlFor="reminder-time">Reminder Time</Label>
              <Input
                id="reminder-time"
                type="time"
                value={settings.dailyReminderTime}
                onChange={(e) => 
                  setSettings(current => ({ ...current!, dailyReminderTime: e.target.value }))
                }
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="sound-enabled">Sound Notifications</Label>
                <p className="text-sm text-muted-foreground">
                  Play a sound with notifications
                </p>
              </div>
              <Switch
                id="sound-enabled"
                checked={settings.soundEnabled}
                onCheckedChange={(checked) => 
                  setSettings(current => ({ ...current!, soundEnabled: checked }))
                }
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="desktop-notifications">Desktop Notifications</Label>
                <p className="text-sm text-muted-foreground">
                  Show browser notifications
                </p>
              </div>
              <Switch
                id="desktop-notifications"
                checked={settings.desktopNotifications}
                disabled={!hasPermission}
                onCheckedChange={(checked) => 
                  setSettings(current => ({ ...current!, desktopNotifications: checked }))
                }
              />
            </div>

            {!hasPermission && (
              <Button 
                variant="outline" 
                onClick={requestNotificationPermission}
                className="w-full"
              >
                Grant Notification Permissions
              </Button>
            )}

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="missed-reminders">Missed Day Reminders</Label>
                <p className="text-sm text-muted-foreground">
                  Get reminded if you miss a day
                </p>
              </div>
              <Switch
                id="missed-reminders"
                checked={settings.missedDayReminders}
                onCheckedChange={(checked) => 
                  setSettings(current => ({ ...current!, missedDayReminders: checked }))
                }
              />
            </div>

            {hasPermission && (
              <Button 
                variant="secondary" 
                onClick={sendTestNotification}
                className="w-full"
              >
                <Check size={16} className="mr-2" />
                Send Test Notification
              </Button>
            )}
          </>
        )}
      </CardContent>
    </Card>
  )
}
