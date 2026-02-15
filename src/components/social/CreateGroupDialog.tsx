import { useState, useEffect } from 'react'
import { useKV } from '@github/spark/hooks'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Checkbox } from '@/components/ui/checkbox'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Globe, Users, Lock, ShieldCheck } from '@phosphor-icons/react'
import type { GroupDiscussion, UserConnection } from '@/lib/types'
import { toast } from 'sonner'

interface CreateGroupDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export default function CreateGroupDialog({ open, onOpenChange }: CreateGroupDialogProps) {
  const [currentUserId, setCurrentUserId] = useState<string>('')
  const [currentUserName, setCurrentUserName] = useState<string>('')
  const [groups = [], setGroups] = useKV<GroupDiscussion[]>('group-discussions', [])
  const [friends = []] = useKV<UserConnection[]>('user-friends', [])
  
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [topic, setTopic] = useState('')
  const [privacy, setPrivacy] = useState<'public' | 'friends-only' | 'invite-only'>('friends-only')
  const [selectedMembers, setSelectedMembers] = useState<string[]>([])
  const [restrictedPosting, setRestrictedPosting] = useState(false)

  useEffect(() => {
    const fetchUser = async () => {
      const user = await window.spark.user()
      setCurrentUserId(user?.id?.toString() || 'anonymous')
      setCurrentUserName(user?.login || 'Anonymous')
    }
    fetchUser()
  }, [])

  const handleCreate = () => {
    if (!name.trim()) {
      toast.error('Please enter a group name')
      return
    }

    const newGroup: GroupDiscussion = {
      id: `group-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: name.trim(),
      description: description.trim(),
      createdBy: currentUserId,
      createdByName: currentUserName,
      memberIds: [currentUserId, ...selectedMembers],
      members: [
        {
          userId: currentUserId,
          userName: currentUserName,
          role: 'admin',
          joinedAt: Date.now()
        },
        ...selectedMembers.map(memberId => {
          const friend = friends.find(f => f.userId === memberId)
          return {
            userId: memberId,
            userName: friend?.userName || 'Unknown',
            userAvatar: friend?.userAvatar,
            role: 'member' as const,
            joinedAt: Date.now()
          }
        })
      ],
      topic: topic.trim() || undefined,
      privacy,
      lastMessageAt: Date.now(),
      unreadCount: {},
      createdAt: Date.now(),
      pinnedMessageIds: [],
      settings: {
        allowInvites: true,
        anyoneCanPost: !restrictedPosting,
        moderationEnabled: false
      }
    }

    setGroups((currentGroups) => [...(currentGroups || []), newGroup])
    
    toast.success(`Created group "${name}"`)
    
    setName('')
    setDescription('')
    setTopic('')
    setPrivacy('friends-only')
    setSelectedMembers([])
    setRestrictedPosting(false)
    onOpenChange(false)
  }

  const toggleMember = (userId: string) => {
    setSelectedMembers(prev =>
      prev.includes(userId)
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    )
  }

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Create Group Discussion</DialogTitle>
          <DialogDescription>
            Start a Bible study group with multiple friends to discuss scripture together
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="flex-1 pr-4">
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <Label htmlFor="group-name">Group Name *</Label>
              <Input
                id="group-name"
                placeholder="e.g., Gospel of John Study"
                value={name}
                onChange={(e) => setName(e.target.value)}
                maxLength={50}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="group-description">Description</Label>
              <Textarea
                id="group-description"
                placeholder="What will this group discuss?"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                maxLength={200}
                rows={3}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="group-topic">Topic (Optional)</Label>
              <Input
                id="group-topic"
                placeholder="e.g., Prophecy, Parables, Romans"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                maxLength={30}
              />
            </div>

            <div className="space-y-3">
              <Label>Privacy</Label>
              <RadioGroup value={privacy} onValueChange={(value: any) => setPrivacy(value)}>
                <div className="flex items-start space-x-3 p-3 rounded-lg border hover:bg-muted/50 transition-colors">
                  <RadioGroupItem value="public" id="privacy-public" className="mt-1" />
                  <div className="flex-1">
                    <label
                      htmlFor="privacy-public"
                      className="flex items-center gap-2 font-medium cursor-pointer mb-1"
                    >
                      <Globe size={18} weight="fill" className="text-primary" />
                      Public
                    </label>
                    <p className="text-sm text-muted-foreground">
                      Anyone can find and join this group
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3 p-3 rounded-lg border hover:bg-muted/50 transition-colors">
                  <RadioGroupItem value="friends-only" id="privacy-friends" className="mt-1" />
                  <div className="flex-1">
                    <label
                      htmlFor="privacy-friends"
                      className="flex items-center gap-2 font-medium cursor-pointer mb-1"
                    >
                      <Users size={18} weight="fill" className="text-primary" />
                      Friends Only
                    </label>
                    <p className="text-sm text-muted-foreground">
                      Only your friends can see and join this group
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3 p-3 rounded-lg border hover:bg-muted/50 transition-colors">
                  <RadioGroupItem value="invite-only" id="privacy-invite" className="mt-1" />
                  <div className="flex-1">
                    <label
                      htmlFor="privacy-invite"
                      className="flex items-center gap-2 font-medium cursor-pointer mb-1"
                    >
                      <Lock size={18} weight="fill" className="text-primary" />
                      Invite Only
                    </label>
                    <p className="text-sm text-muted-foreground">
                      Members can only join by invitation
                    </p>
                  </div>
                </div>
              </RadioGroup>
            </div>

            <div className="space-y-3">
              <Label>Group Settings</Label>
              <div className="flex items-center justify-between p-3 rounded-lg border">
                <div className="space-y-0.5 flex-1">
                  <div className="flex items-center gap-2">
                    <ShieldCheck size={18} weight="fill" className="text-amber-500" />
                    <Label htmlFor="restricted-posting" className="font-medium cursor-pointer">
                      Restricted Group
                    </Label>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Only admins and moderators can post messages
                  </p>
                </div>
                <Switch
                  id="restricted-posting"
                  checked={restrictedPosting}
                  onCheckedChange={setRestrictedPosting}
                />
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label>Invite Friends</Label>
                <Badge variant="outline">
                  {selectedMembers.length} selected
                </Badge>
              </div>
              
              {friends.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No friends to invite yet. Add friends first!
                </p>
              ) : (
                <div className="space-y-2 max-h-64 overflow-y-auto rounded-lg border p-2">
                  {friends.map(friend => (
                    <div
                      key={friend.userId}
                      className="flex items-center gap-3 p-2 rounded-lg hover:bg-muted/50 transition-colors"
                    >
                      <Checkbox
                        id={`friend-${friend.userId}`}
                        checked={selectedMembers.includes(friend.userId)}
                        onCheckedChange={() => toggleMember(friend.userId)}
                      />
                      <label
                        htmlFor={`friend-${friend.userId}`}
                        className="flex items-center gap-3 flex-1 cursor-pointer"
                      >
                        <Avatar className="h-10 w-10">
                          <AvatarFallback>{getInitials(friend.userName)}</AvatarFallback>
                        </Avatar>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium truncate">{friend.userName}</p>
                          <p className="text-xs text-muted-foreground">
                            Friend since {new Date(friend.connectedAt).toLocaleDateString()}
                          </p>
                        </div>
                      </label>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </ScrollArea>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleCreate} disabled={!name.trim()}>
            Create Group
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
