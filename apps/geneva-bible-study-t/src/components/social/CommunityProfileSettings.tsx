import { useState, useEffect } from 'react'
import { useKV } from '@github/spark/hooks'
import { User, Lock, Eye, EyeSlash, CheckCircle } from '@phosphor-icons/react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Separator } from '@/components/ui/separator'
import type { CommunityProfile } from '@/lib/types'
import { toast } from 'sonner'

export default function CommunityProfileSettings() {
  const [profile, setProfile] = useKV<CommunityProfile>('community-profile', undefined as any)
  const [bio, setBio] = useState('')
  const [location, setLocation] = useState('')
  const [denomination, setDenomination] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    initializeProfile()
  }, [])

  const initializeProfile = async () => {
    const user = await window.spark.user()
    
    if (!profile) {
      const newProfile: CommunityProfile = {
        userId: user?.id?.toString() || 'anonymous',
        userName: user?.login || 'Reader',
        userAvatar: user?.avatarUrl,
        bio: '',
        location: '',
        denomination: '',
        favoriteBooks: [],
        readingGoals: {
          currentStreak: 0,
          longestStreak: 0,
          totalChaptersRead: 0,
          plansCompleted: 0
        },
        privacy: {
          profileVisible: true,
          showReadingProgress: true,
          showFriendsList: true,
          allowFriendRequests: true
        },
        createdAt: Date.now(),
        updatedAt: Date.now()
      }
      setProfile(newProfile)
    } else {
      setBio(profile.bio || '')
      setLocation(profile.location || '')
      setDenomination(profile.denomination || '')
    }
    
    setLoading(false)
  }

  const handleSave = () => {
    setProfile((current) => ({
      ...current!,
      bio: bio.trim(),
      location: location.trim(),
      denomination: denomination.trim(),
      updatedAt: Date.now()
    }))
    toast.success('Profile updated successfully!')
  }

  const togglePrivacySetting = (key: keyof CommunityProfile['privacy']) => {
    setProfile((current) => ({
      ...current!,
      privacy: {
        ...current!.privacy,
        [key]: !current!.privacy[key]
      },
      updatedAt: Date.now()
    }))
  }

  if (loading || !profile) {
    return (
      <div className="flex items-center justify-center p-12">
        <p className="text-muted-foreground">Loading profile...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User size={20} weight="duotone" className="text-primary" />
            Community Profile
          </CardTitle>
          <CardDescription>
            Customize how you appear to other users in the community
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="bio">Bio</Label>
            <Textarea
              id="bio"
              placeholder="Share a bit about your faith journey..."
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              rows={3}
              maxLength={200}
            />
            <p className="text-xs text-muted-foreground text-right">
              {bio.length}/200
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="location">Location</Label>
              <Input
                id="location"
                placeholder="City, State"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                maxLength={50}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="denomination">Denomination</Label>
              <Input
                id="denomination"
                placeholder="e.g., Baptist, Catholic, etc."
                value={denomination}
                onChange={(e) => setDenomination(e.target.value)}
                maxLength={50}
              />
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <Button onClick={handleSave} className="gap-2">
              <CheckCircle size={16} weight="duotone" />
              Save Profile
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lock size={20} weight="duotone" className="text-primary" />
            Privacy Settings
          </CardTitle>
          <CardDescription>
            Control what information is visible to other users
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="text-base">Profile Visible</Label>
              <p className="text-sm text-muted-foreground">
                Allow other users to view your profile
              </p>
            </div>
            <Switch
              checked={profile.privacy.profileVisible}
              onCheckedChange={() => togglePrivacySetting('profileVisible')}
            />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="text-base">Show Reading Progress</Label>
              <p className="text-sm text-muted-foreground">
                Display your reading stats and activity
              </p>
            </div>
            <Switch
              checked={profile.privacy.showReadingProgress}
              onCheckedChange={() => togglePrivacySetting('showReadingProgress')}
              disabled={!profile.privacy.profileVisible}
            />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="text-base">Show Friends List</Label>
              <p className="text-sm text-muted-foreground">
                Let others see who you're connected with
              </p>
            </div>
            <Switch
              checked={profile.privacy.showFriendsList}
              onCheckedChange={() => togglePrivacySetting('showFriendsList')}
              disabled={!profile.privacy.profileVisible}
            />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="text-base">Allow Friend Requests</Label>
              <p className="text-sm text-muted-foreground">
                Enable others to send you friend requests
              </p>
            </div>
            <Switch
              checked={profile.privacy.allowFriendRequests}
              onCheckedChange={() => togglePrivacySetting('allowFriendRequests')}
              disabled={!profile.privacy.profileVisible}
            />
          </div>
        </CardContent>
      </Card>

      <Card className="bg-muted/30">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              {profile.privacy.profileVisible ? (
                <Eye size={20} className="text-primary" weight="duotone" />
              ) : (
                <EyeSlash size={20} className="text-muted-foreground" weight="duotone" />
              )}
            </div>
            <div className="flex-1">
              <p className="font-semibold mb-1">
                {profile.privacy.profileVisible ? 'Profile is Public' : 'Profile is Private'}
              </p>
              <p className="text-sm text-muted-foreground">
                {profile.privacy.profileVisible
                  ? 'Other users can discover and view your profile. Your reading journey and activity are visible based on your privacy settings.'
                  : 'Your profile is hidden from other users. Only you can see your stats and activity.'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
