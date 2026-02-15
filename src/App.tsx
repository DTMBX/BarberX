import { useState } from 'react'
import { useKV } from '@github/spark/hooks'
import { BookOpen, Books, Columns, MagnifyingGlass, Clock, Gear, CalendarCheck, Users, ChatCircle, UsersThree, PushPin, Moon, Sun } from '@phosphor-icons/react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useIsMobile } from '@/hooks/use-mobile'
import { useKeyboardShortcuts } from '@/hooks/use-keyboard-shortcuts'
import { useDarkMode } from '@/hooks/use-dark-mode'
import { useAutoDarkMode } from '@/hooks/use-auto-dark-mode'
import KeyboardShortcutsDialog from '@/components/KeyboardShortcutsDialog'
import HomeView from '@/components/views/HomeView'
import LibraryView from '@/components/views/LibraryView'
import CompareView from '@/components/views/CompareView'
import SearchView from '@/components/views/SearchView'
import TimelineView from '@/components/views/TimelineView'
import SettingsView from '@/components/views/SettingsView'
import ReadingPlanView from '@/components/views/ReadingPlanView'
import SocialView from '@/components/views/SocialView'
import MessagesView from '@/components/views/MessagesView'
import GroupDiscussionsView from '@/components/views/GroupDiscussionsView'
import PinnedMessagesView from '@/components/views/PinnedMessagesView'
import ReaderView from '@/components/reader/ReaderView'
import type { UserProfile, FriendRequest, Conversation, GroupDiscussion } from '@/lib/types'

function App() {
  const isMobile = useIsMobile()
  const isDarkMode = useDarkMode()
  useAutoDarkMode()
  const [activeTab, setActiveTab] = useState('home')
  const [showKeyboardShortcuts, setShowKeyboardShortcuts] = useState(false)
  
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

  const [friendRequests = []] = useKV<FriendRequest[]>('friend-requests', [])
  const [conversations = []] = useKV<Conversation[]>('conversations', [])
  const [groups = []] = useKV<GroupDiscussion[]>('group-discussions', [])
  const [currentUserId, setCurrentUserId] = useState<string>('')
  const [messageNavigation, setMessageNavigation] = useState<{ friendId: string; verseRef?: any } | null>(null)

  useState(() => {
    const fetchUser = async () => {
      const user = await window.spark.user()
      setCurrentUserId(user?.id?.toString() || 'anonymous')
    }
    fetchUser()
  })

  const pendingRequestCount = friendRequests.filter(req => req.status === 'pending').length
  const unreadMessagesCount = conversations.reduce((total, conv) => {
    return total + (conv.unreadCount[currentUserId] || 0)
  }, 0)
  const userGroups = groups.filter(g => g.memberIds.includes(currentUserId))
  const unreadGroupsCount = userGroups.reduce((total, group) => {
    return total + (group.unreadCount[currentUserId] || 0)
  }, 0)
  
  const groupsWithNewPins = userGroups.filter(group => group.pinnedMessageIds.length > 0).length

  const handleNavigateToReader = (bookId: string, chapter: number) => {
    setActiveTab('reader')
    setTimeout(() => {
      const event = new CustomEvent('navigate-to-passage', {
        detail: { bookId, chapter }
      })
      window.dispatchEvent(event)
    }, 100)
  }

  const handleNavigateToMessages = (friendId: string, verseRef?: any) => {
    setMessageNavigation({ friendId, verseRef })
    setActiveTab('messages')
  }

  const handleNavigateToGroup = (groupId: string, groupName: string) => {
    setActiveTab('groups')
  }

  useKeyboardShortcuts([
    {
      key: '/',
      ctrl: true,
      description: 'Show keyboard shortcuts',
      action: () => setShowKeyboardShortcuts(true)
    },
    {
      key: 'd',
      ctrl: true,
      description: 'Toggle dark mode (manual override)',
      action: () => {
        setUserProfile(current => ({
          ...current!,
          preferences: {
            ...current!.preferences,
            nightMode: !current!.preferences.nightMode
          }
        }))
      }
    },
    {
      key: ',',
      ctrl: true,
      description: 'Open settings',
      action: () => setActiveTab('settings')
    },
    {
      key: 'k',
      ctrl: true,
      description: 'Open search',
      action: () => setActiveTab('search')
    },
    {
      key: '1',
      description: 'Go to Home',
      action: () => setActiveTab('home')
    },
    {
      key: '2',
      description: 'Go to Reader',
      action: () => setActiveTab('reader')
    },
    {
      key: '3',
      description: 'Go to Library',
      action: () => setActiveTab('library')
    },
    {
      key: '4',
      description: 'Go to Compare',
      action: () => setActiveTab('compare')
    },
    {
      key: '5',
      description: 'Go to Search',
      action: () => setActiveTab('search')
    },
    {
      key: '6',
      description: 'Go to Timeline',
      action: () => setActiveTab('timeline')
    },
    {
      key: '7',
      description: 'Go to Reading Plans',
      action: () => setActiveTab('reading-plan')
    },
    {
      key: '8',
      description: 'Go to Social',
      action: () => setActiveTab('social')
    },
    {
      key: '9',
      description: 'Go to Messages',
      action: () => setActiveTab('messages')
    }
  ])

  return (
    <div className="h-screen flex flex-col bg-background">
      <header className="border-b border-border bg-card px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Books size={28} weight="duotone" className="text-primary" />
          <h1 className="text-2xl font-bold text-primary tracking-tight" style={{ fontFamily: 'var(--font-heading)' }}>
            Geneva Bible Study
          </h1>
        </div>
        <div className="flex items-center gap-2">
          {!isMobile && groupsWithNewPins > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setActiveTab('pinned-messages')}
              className="gap-2"
            >
              <PushPin size={18} weight="fill" />
              <span>{groupsWithNewPins} group{groupsWithNewPins !== 1 ? 's' : ''} with pins</span>
            </Button>
          )}
          <button
            onClick={() => {
              setUserProfile(current => ({
                ...current!,
                preferences: {
                  ...current!.preferences,
                  nightMode: !current!.preferences.nightMode
                }
              }))
            }}
            className="p-2 hover:bg-muted rounded-md transition-colors"
            aria-label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
            title={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {isDarkMode ? (
              <Sun size={24} weight="duotone" className="text-muted-foreground" />
            ) : (
              <Moon size={24} weight="duotone" className="text-muted-foreground" />
            )}
          </button>
          {!isMobile && (
            <button
              onClick={() => setActiveTab('settings')}
              className="p-2 hover:bg-muted rounded-md transition-colors"
              aria-label="Settings"
            >
              <Gear size={24} weight="duotone" className="text-muted-foreground" />
            </button>
          )}
        </div>
      </header>

      <div className="flex-1 overflow-hidden">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
          {isMobile ? (
            <>
              <div className="flex-1 overflow-auto">
                <TabsContent value="home" className="mt-0 h-full">
                  <HomeView 
                    userProfile={userProfile!}
                    onNavigateToReader={handleNavigateToReader}
                    onNavigateToMessages={handleNavigateToMessages}
                  />
                </TabsContent>
                <TabsContent value="reader" className="mt-0 h-full">
                  <ReaderView userProfile={userProfile!} />
                </TabsContent>
                <TabsContent value="library" className="mt-0 h-full">
                  <LibraryView />
                </TabsContent>
                <TabsContent value="compare" className="mt-0 h-full">
                  <CompareView userProfile={userProfile!} />
                </TabsContent>
                <TabsContent value="search" className="mt-0 h-full">
                  <SearchView />
                </TabsContent>
                <TabsContent value="timeline" className="mt-0 h-full">
                  <TimelineView />
                </TabsContent>
                <TabsContent value="reading-plan" className="mt-0 h-full">
                  <ReadingPlanView onNavigateToReader={handleNavigateToReader} />
                </TabsContent>
                <TabsContent value="social" className="mt-0 h-full">
                  <SocialView onNavigateToMessages={handleNavigateToMessages} />
                </TabsContent>
                <TabsContent value="messages" className="mt-0 h-full">
                  <MessagesView initialNavigation={messageNavigation} onClearNavigation={() => setMessageNavigation(null)} />
                </TabsContent>
                <TabsContent value="settings" className="mt-0 h-full">
                  <SettingsView userProfile={userProfile!} />
                </TabsContent>
              </div>

              <TabsList className="w-full h-16 rounded-none border-t grid grid-cols-9 bg-card">
                <TabsTrigger value="home" className="flex-col gap-1 data-[state=active]:text-primary">
                  <BookOpen size={24} weight="duotone" />
                  <span className="text-xs">Home</span>
                </TabsTrigger>
                <TabsTrigger value="library" className="flex-col gap-1 data-[state=active]:text-primary">
                  <Books size={24} weight="duotone" />
                  <span className="text-xs">Library</span>
                </TabsTrigger>
                <TabsTrigger value="reading-plan" className="flex-col gap-1 data-[state=active]:text-primary">
                  <CalendarCheck size={24} weight="duotone" />
                  <span className="text-xs">Plans</span>
                </TabsTrigger>
                <TabsTrigger value="compare" className="flex-col gap-1 data-[state=active]:text-primary">
                  <Columns size={24} weight="duotone" />
                  <span className="text-xs">Compare</span>
                </TabsTrigger>
                <TabsTrigger value="search" className="flex-col gap-1 data-[state=active]:text-primary">
                  <MagnifyingGlass size={24} weight="duotone" />
                  <span className="text-xs">Search</span>
                </TabsTrigger>
                <TabsTrigger value="timeline" className="flex-col gap-1 data-[state=active]:text-primary">
                  <Clock size={24} weight="duotone" />
                  <span className="text-xs">Timeline</span>
                </TabsTrigger>
                <TabsTrigger value="social" className="flex-col gap-1 data-[state=active]:text-primary relative">
                  <Users size={24} weight="duotone" />
                  <span className="text-xs">Social</span>
                  {pendingRequestCount > 0 && (
                    <Badge className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-[10px] bg-destructive">
                      {pendingRequestCount}
                    </Badge>
                  )}
                </TabsTrigger>
                <TabsTrigger value="messages" className="flex-col gap-1 data-[state=active]:text-primary relative">
                  <ChatCircle size={24} weight="duotone" />
                  <span className="text-xs">Chat</span>
                  {unreadMessagesCount > 0 && (
                    <Badge className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-[10px] bg-primary">
                      {unreadMessagesCount}
                    </Badge>
                  )}
                </TabsTrigger>
                <TabsTrigger value="groups" className="flex-col gap-1 data-[state=active]:text-primary relative">
                  <UsersThree size={24} weight="duotone" />
                  <span className="text-xs">Groups</span>
                  {(unreadGroupsCount > 0 || groupsWithNewPins > 0) && (
                    <Badge className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-[10px] bg-primary">
                      {unreadGroupsCount > 0 ? (unreadGroupsCount > 9 ? '9+' : unreadGroupsCount) : groupsWithNewPins}
                    </Badge>
                  )}
                </TabsTrigger>
              </TabsList>
            </>
          ) : (
            <div className="flex h-full">
              <TabsList className="w-60 flex-col gap-2 p-4 rounded-none border-r bg-card items-stretch justify-start h-full">
                <TabsTrigger value="home" className="justify-start gap-3 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
                  <BookOpen size={24} weight="duotone" />
                  <span>Home</span>
                </TabsTrigger>
                <TabsTrigger value="reader" className="justify-start gap-3 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
                  <BookOpen size={24} weight="duotone" />
                  <span>Reader</span>
                </TabsTrigger>
                <TabsTrigger value="library" className="justify-start gap-3 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
                  <Books size={24} weight="duotone" />
                  <span>Library</span>
                </TabsTrigger>
                <TabsTrigger value="compare" className="justify-start gap-3 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
                  <Columns size={24} weight="duotone" />
                  <span>Compare</span>
                </TabsTrigger>
                <TabsTrigger value="search" className="justify-start gap-3 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
                  <MagnifyingGlass size={24} weight="duotone" />
                  <span>Search</span>
                </TabsTrigger>
                <TabsTrigger value="timeline" className="justify-start gap-3 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
                  <Clock size={24} weight="duotone" />
                  <span>Timeline</span>
                </TabsTrigger>
                <TabsTrigger value="reading-plan" className="justify-start gap-3 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
                  <CalendarCheck size={24} weight="duotone" />
                  <span>Reading Plans</span>
                </TabsTrigger>
                <TabsTrigger value="social" className="justify-start gap-3 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground relative">
                  <Users size={24} weight="duotone" />
                  <span>Social</span>
                  {pendingRequestCount > 0 && (
                    <Badge className="ml-auto h-6 w-6 flex items-center justify-center p-0 text-xs bg-destructive">
                      {pendingRequestCount}
                    </Badge>
                  )}
                </TabsTrigger>
                <TabsTrigger value="messages" className="justify-start gap-3 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground relative">
                  <ChatCircle size={24} weight="duotone" />
                  <span>Messages</span>
                  {unreadMessagesCount > 0 && (
                    <Badge className="ml-auto h-6 w-6 flex items-center justify-center p-0 text-xs bg-primary">
                      {unreadMessagesCount}
                    </Badge>
                  )}
                </TabsTrigger>
                <TabsTrigger value="groups" className="justify-start gap-3 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground relative">
                  <UsersThree size={24} weight="duotone" />
                  <span>Groups</span>
                  {(unreadGroupsCount > 0 || groupsWithNewPins > 0) && (
                    <Badge className="ml-auto h-6 w-6 flex items-center justify-center p-0 text-xs bg-primary">
                      {unreadGroupsCount > 0 ? (unreadGroupsCount > 9 ? '9+' : unreadGroupsCount) : groupsWithNewPins}
                    </Badge>
                  )}
                </TabsTrigger>
                <TabsTrigger value="pinned-messages" className="justify-start gap-3 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
                  <PushPin size={24} weight="duotone" />
                  <span>Pinned Messages</span>
                  {groupsWithNewPins > 0 && (
                    <Badge className="ml-auto h-6 w-6 flex items-center justify-center p-0 text-xs bg-accent">
                      {groupsWithNewPins}
                    </Badge>
                  )}
                </TabsTrigger>
                <div className="flex-1" />
                <TabsTrigger value="settings" className="justify-start gap-3 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
                  <Gear size={24} weight="duotone" />
                  <span>Settings</span>
                </TabsTrigger>
              </TabsList>

              <div className="flex-1 overflow-auto">
                <TabsContent value="home" className="mt-0 h-full">
                  <HomeView 
                    userProfile={userProfile!}
                    onNavigateToReader={handleNavigateToReader}
                    onNavigateToMessages={handleNavigateToMessages}
                  />
                </TabsContent>
                <TabsContent value="reader" className="mt-0 h-full">
                  <ReaderView userProfile={userProfile!} />
                </TabsContent>
                <TabsContent value="library" className="mt-0 h-full">
                  <LibraryView />
                </TabsContent>
                <TabsContent value="compare" className="mt-0 h-full">
                  <CompareView userProfile={userProfile!} />
                </TabsContent>
                <TabsContent value="search" className="mt-0 h-full">
                  <SearchView />
                </TabsContent>
                <TabsContent value="timeline" className="mt-0 h-full">
                  <TimelineView />
                </TabsContent>
                <TabsContent value="reading-plan" className="mt-0 h-full">
                  <ReadingPlanView onNavigateToReader={handleNavigateToReader} />
                </TabsContent>
                <TabsContent value="social" className="mt-0 h-full">
                  <SocialView onNavigateToMessages={handleNavigateToMessages} />
                </TabsContent>
                <TabsContent value="messages" className="mt-0 h-full">
                  <MessagesView initialNavigation={messageNavigation} onClearNavigation={() => setMessageNavigation(null)} />
                </TabsContent>
                <TabsContent value="groups" className="mt-0 h-full">
                  <GroupDiscussionsView />
                </TabsContent>
                <TabsContent value="pinned-messages" className="mt-0 h-full">
                  <PinnedMessagesView 
                    onBack={() => setActiveTab('groups')}
                    onNavigateToGroup={handleNavigateToGroup}
                  />
                </TabsContent>
                <TabsContent value="settings" className="mt-0 h-full">
                  <SettingsView userProfile={userProfile!} />
                </TabsContent>
              </div>
            </div>
          )}
        </Tabs>
      </div>

      <KeyboardShortcutsDialog
        open={showKeyboardShortcuts}
        onOpenChange={setShowKeyboardShortcuts}
      />
    </div>
  )
}

export default App
