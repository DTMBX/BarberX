import { useState } from 'react'
import { useKV } from '@github/spark/hooks'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Calendar, CheckCircle, Circle, BookOpen, Play, Pause, ArrowCounterClockwise, CalendarBlank, ListChecks, Plus, Bell, Trash, ShareNetwork, Trophy } from '@phosphor-icons/react'
import { readingPlans, getBookDisplayName } from '@/lib/reading-plans'
import type { UserReadingPlan, ReadingPlan } from '@/lib/types'
import { toast } from 'sonner'
import CustomPlanBuilder from './CustomPlanBuilder'
import NotificationSettingsPanel from './NotificationSettingsPanel'
import ShareProgressDialog from '@/components/social/ShareProgressDialog'
import { trackUserActivity, updateCurrentStreak } from '@/lib/community-utils'

interface ReadingPlanViewProps {
  onNavigateToReader?: (bookId: string, chapter: number) => void
}

export default function ReadingPlanView({ onNavigateToReader }: ReadingPlanViewProps) {
  const [activeUserPlans = [], setActiveUserPlans] = useKV<UserReadingPlan[]>('user-reading-plans', [])
  const [customPlans = [], setCustomPlans] = useKV<ReadingPlan[]>('custom-reading-plans', [])
  const [selectedPlanId, setSelectedPlanId] = useState<string | null>(null)
  const [showCustomPlanBuilder, setShowCustomPlanBuilder] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)
  const [shareDialogOpen, setShareDialogOpen] = useState(false)
  const [shareDialogData, setShareDialogData] = useState<{
    type: 'milestone' | 'plan-complete' | 'streak'
    title: string
    description: string
    planName?: string
    planId?: string
    daysCompleted?: number
    totalDays?: number
    streakDays?: number
  } | null>(null)

  const allPlans = [...readingPlans, ...(customPlans || [])]
  const selectedUserPlan = activeUserPlans?.find(p => p.planId === selectedPlanId)
  const selectedPlan = allPlans.find(p => p.id === selectedPlanId)

  const handleCreateCustomPlan = (plan: ReadingPlan) => {
    setCustomPlans((current) => [...(current || []), plan])
    setShowCustomPlanBuilder(false)
    toast.success('Custom plan created! Start it from the available plans.')
  }

  const handleDeleteCustomPlan = (planId: string) => {
    if (!confirm('Delete this custom plan? This cannot be undone.')) return
    
    setCustomPlans((current) => (current || []).filter(p => p.id !== planId))
    setActiveUserPlans((current) => (current || []).filter(p => p.planId !== planId))
    
    if (selectedPlanId === planId) {
      setSelectedPlanId(null)
    }
    
    toast.success('Custom plan deleted')
  }

  const startPlan = (planId: string) => {
    const existingPlan = activeUserPlans?.find(p => p.planId === planId)
    
    if (existingPlan) {
      setSelectedPlanId(planId)
      toast.success('Resumed reading plan')
      return
    }

    const newUserPlan: UserReadingPlan = {
      id: `plan-${Date.now()}`,
      userId: 'default-user',
      planId,
      startDate: Date.now(),
      currentDay: 1,
      completedDays: [],
      paused: false,
      notes: {},
      reminderEnabled: false
    }

    setActiveUserPlans(current => [...(current || []), newUserPlan])
    setSelectedPlanId(planId)
    toast.success('Reading plan started!')
  }

  const openTodaysReading = () => {
    if (!selectedPlan || !selectedUserPlan || !onNavigateToReader) return
    
    const currentDayReading = getCurrentDayReading()
    if (!currentDayReading || currentDayReading.readings.length === 0) return
    
    const firstReading = currentDayReading.readings[0]
    onNavigateToReader(firstReading.workId, firstReading.chapterNumber)
    toast.success('Opening today\'s reading in Bible Reader')
  }

  const markDayComplete = async (day: number) => {
    const wasCompleted = selectedUserPlan?.completedDays.includes(day) || false
    
    setActiveUserPlans(current => 
      (current || []).map(plan => {
        if (plan.planId === selectedPlanId) {
          const isCompleted = plan.completedDays.includes(day)
          const newCompletedDays = isCompleted
            ? plan.completedDays.filter(d => d !== day)
            : [...plan.completedDays, day].sort((a, b) => a - b)
          
          return {
            ...plan,
            completedDays: newCompletedDays,
            currentDay: Math.max(...newCompletedDays, plan.currentDay)
          }
        }
        return plan
      })
    )
    
    if (!wasCompleted) {
      const dayReading = selectedPlan?.days.find(d => d.day === day)
      if (dayReading && dayReading.readings.length > 0) {
        const firstReading = dayReading.readings[0]
        await trackUserActivity('chapter-read', {
          bookName: getBookDisplayName(firstReading.workId),
          chapterNumber: firstReading.chapterNumber,
          planName: selectedPlan?.name
        }, 'friends')
      }

      await updateCurrentStreak()

      const newCompletedCount = (selectedUserPlan?.completedDays.length || 0) + 1
      const totalDays = selectedPlan?.duration || 0
      
      if (newCompletedCount === totalDays) {
        await trackUserActivity('plan-completed', {
          planName: selectedPlan?.name,
          planId: selectedPlanId || '',
          daysCompleted: totalDays
        }, 'friends')

        setShareDialogData({
          type: 'plan-complete',
          title: 'Reading Plan Complete!',
          description: `You've completed the ${selectedPlan?.name} reading plan!`,
          planName: selectedPlan?.name,
          planId: selectedPlanId || undefined,
          daysCompleted: totalDays,
          totalDays: totalDays
        })
        setShareDialogOpen(true)
      } else if (newCompletedCount % 7 === 0) {
        setShareDialogData({
          type: 'streak',
          title: `${newCompletedCount} Days Complete!`,
          description: `You've maintained your reading streak for ${newCompletedCount} days!`,
          planName: selectedPlan?.name,
          streakDays: newCompletedCount
        })
        setShareDialogOpen(true)
      } else if ([30, 50, 100].includes(newCompletedCount)) {
        await trackUserActivity('milestone-achieved', {
          planName: selectedPlan?.name,
          daysCompleted: newCompletedCount
        }, 'friends')

        setShareDialogData({
          type: 'milestone',
          title: `${newCompletedCount} Days Milestone!`,
          description: `You've completed ${newCompletedCount} days of reading!`,
          planName: selectedPlan?.name,
          daysCompleted: newCompletedCount,
          totalDays: totalDays
        })
        setShareDialogOpen(true)
      }
      
      toast.success('Day completed! 🎉')
    } else {
      toast.success('Day marked incomplete')
    }
  }

  const togglePause = () => {
    setActiveUserPlans(current =>
      (current || []).map(plan => 
        plan.planId === selectedPlanId 
          ? { ...plan, paused: !plan.paused }
          : plan
      )
    )
    toast.success(selectedUserPlan?.paused ? 'Plan resumed' : 'Plan paused')
  }

  const resetPlan = () => {
    if (!confirm('Are you sure you want to reset this plan? All progress will be lost.')) return
    
    setActiveUserPlans(current =>
      (current || []).map(plan =>
        plan.planId === selectedPlanId
          ? {
              ...plan,
              currentDay: 1,
              completedDays: [],
              startDate: Date.now(),
              paused: false,
              notes: {}
            }
          : plan
      )
    )
    toast.success('Plan reset')
  }

  const getCurrentDayReading = () => {
    if (!selectedPlan || !selectedUserPlan) return null
    
    const nextIncompleteDay = selectedPlan.days.find(
      day => !selectedUserPlan.completedDays.includes(day.day)
    )
    
    return nextIncompleteDay || selectedPlan.days[selectedPlan.days.length - 1]
  }

  const getProgressPercentage = () => {
    if (!selectedUserPlan || !selectedPlan) return 0
    return (selectedUserPlan.completedDays.length / selectedPlan.duration) * 100
  }

  const getDaysElapsed = () => {
    if (!selectedUserPlan) return 0
    return Math.floor((Date.now() - selectedUserPlan.startDate) / (1000 * 60 * 60 * 24))
  }

  if (!selectedPlanId || !selectedPlan || !selectedUserPlan) {
    return (
      <>
        {shareDialogOpen && shareDialogData && (
          <ShareProgressDialog
            open={shareDialogOpen}
            onOpenChange={setShareDialogOpen}
            type={shareDialogData.type}
            title={shareDialogData.title}
            description={shareDialogData.description}
            planName={shareDialogData.planName}
            planId={shareDialogData.planId}
            daysCompleted={shareDialogData.daysCompleted}
            totalDays={shareDialogData.totalDays}
            streakDays={shareDialogData.streakDays}
          />
        )}
        <div className="container mx-auto p-6 max-w-6xl">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 text-primary" style={{ fontFamily: 'var(--font-heading)' }}>
            Reading Plans
          </h1>
          <p className="text-muted-foreground">
            Build consistent Bible reading habits with structured daily plans
          </p>
        </div>

        {activeUserPlans.length > 0 && (
          <div className="mb-8">
            <h2 className="text-2xl font-semibold mb-4" style={{ fontFamily: 'var(--font-heading)' }}>
              Your Active Plans
            </h2>
            <div className="grid gap-4 md:grid-cols-2">
              {activeUserPlans.map(userPlan => {
                const plan = allPlans.find(p => p.id === userPlan.planId)
                if (!plan) return null
                
                const progress = (userPlan.completedDays.length / plan.duration) * 100
                
                return (
                  <Card key={userPlan.id} className="cursor-pointer hover:border-primary transition-colors" onClick={() => setSelectedPlanId(plan.id)}>
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle className="text-xl">{plan.name}</CardTitle>
                          <CardDescription className="mt-1">{plan.description}</CardDescription>
                        </div>
                        {userPlan.paused && (
                          <Badge variant="secondary">Paused</Badge>
                        )}
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-muted-foreground">Progress</span>
                            <span className="font-medium">{userPlan.completedDays.length} / {plan.duration} days</span>
                          </div>
                          <Progress value={progress} className="h-2" />
                        </div>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <div className="flex items-center gap-2">
                            <CalendarBlank size={16} />
                            <span>Started {new Date(userPlan.startDate).toLocaleDateString()}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <ListChecks size={16} />
                            <span>{Math.round(progress)}% complete</span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </div>
        )}

        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-semibold" style={{ fontFamily: 'var(--font-heading)' }}>
              Available Plans
            </h2>
            <div className="flex gap-2">
              <Button onClick={() => setShowNotifications(!showNotifications)} variant="outline" size="sm">
                <Bell size={16} className="mr-2" />
                Reminders
              </Button>
              <Button onClick={() => setShowCustomPlanBuilder(true)} variant="default" size="sm">
                <Plus size={16} className="mr-2" />
                Create Custom Plan
              </Button>
            </div>
          </div>

          {showNotifications && (
            <div className="mb-6">
              <NotificationSettingsPanel />
            </div>
          )}
          
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {allPlans.map(plan => {
              const isActive = activeUserPlans.some(up => up.planId === plan.id)
              const isCustom = plan.isCustom
              
              return (
                <Card key={plan.id} className="flex flex-col">
                  <CardHeader>
                    <div className="flex items-start justify-between mb-2">
                      <Badge variant={plan.category === 'chronological' ? 'default' : 'secondary'}>
                        {plan.category}
                      </Badge>
                      <div className="flex gap-2 items-center">
                        <Badge variant="outline">{plan.duration} days</Badge>
                        {isCustom && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0 hover:bg-destructive/10 hover:text-destructive"
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDeleteCustomPlan(plan.id)
                            }}
                          >
                            <Trash size={14} />
                          </Button>
                        )}
                      </div>
                    </div>
                    <CardTitle className="text-xl">{plan.name}</CardTitle>
                    <CardDescription>{plan.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="flex-1 flex flex-col justify-end">
                    <Button 
                      onClick={() => startPlan(plan.id)}
                      variant={isActive ? 'secondary' : 'default'}
                      className="w-full"
                    >
                      <Play size={16} weight="fill" className="mr-2" />
                      {isActive ? 'Continue Plan' : 'Start Plan'}
                    </Button>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>
        </div>
      </>
    )
  }

  const currentDayReading = getCurrentDayReading()
  const progress = getProgressPercentage()
  const daysElapsed = getDaysElapsed()

  return (
    <>
      {shareDialogOpen && shareDialogData && (
        <ShareProgressDialog
          open={shareDialogOpen}
          onOpenChange={setShareDialogOpen}
          type={shareDialogData.type}
          title={shareDialogData.title}
          description={shareDialogData.description}
          planName={shareDialogData.planName}
          planId={shareDialogData.planId}
          daysCompleted={shareDialogData.daysCompleted}
          totalDays={shareDialogData.totalDays}
          streakDays={shareDialogData.streakDays}
        />
      )}
      <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-6">
        <Button variant="ghost" onClick={() => setSelectedPlanId(null)} className="mb-4">
          ← Back to Plans
        </Button>
        
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2 text-primary" style={{ fontFamily: 'var(--font-heading)' }}>
              {selectedPlan.name}
            </h1>
            <p className="text-muted-foreground">{selectedPlan.description}</p>
          </div>
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => {
                setShareDialogData({
                  type: 'milestone',
                  title: `${selectedUserPlan.completedDays.length} Days Complete`,
                  description: `Making progress through ${selectedPlan.name}`,
                  planName: selectedPlan.name,
                  planId: selectedPlanId || undefined,
                  daysCompleted: selectedUserPlan.completedDays.length,
                  totalDays: selectedPlan.duration
                })
                setShareDialogOpen(true)
              }}
            >
              <ShareNetwork size={16} weight="duotone" />
              <span className="ml-2">Share</span>
            </Button>
            <Button variant="outline" size="sm" onClick={togglePause}>
              {selectedUserPlan.paused ? (
                <>
                  <Play size={16} weight="fill" />
                  <span className="ml-2">Resume</span>
                </>
              ) : (
                <>
                  <Pause size={16} weight="fill" />
                  <span className="ml-2">Pause</span>
                </>
              )}
            </Button>
            <Button variant="outline" size="sm" onClick={resetPlan}>
              <ArrowCounterClockwise size={16} />
              <span className="ml-2">Reset</span>
            </Button>
          </div>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3 mb-6">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold mb-2">{Math.round(progress)}%</div>
            <Progress value={progress} className="h-2 mb-2" />
            <p className="text-sm text-muted-foreground">
              {selectedUserPlan.completedDays.length} of {selectedPlan.duration} days
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Days Elapsed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold mb-2">{daysElapsed}</div>
            <p className="text-sm text-muted-foreground">
              Since {new Date(selectedUserPlan.startDate).toLocaleDateString()}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Streak</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold mb-2">
              {selectedUserPlan.completedDays.length > 0 ? '🔥 Active' : 'Start Today'}
            </div>
            <p className="text-sm text-muted-foreground">
              {selectedUserPlan.completedDays.length} days completed
            </p>
          </CardContent>
        </Card>
      </div>

      {currentDayReading && !selectedUserPlan.paused && (
        <Card className="mb-6 border-accent">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen size={24} weight="duotone" className="text-accent" />
              Today's Reading - Day {currentDayReading.day}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {currentDayReading.readings.map((reading, idx) => (
                <div key={idx} className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg cursor-pointer hover:bg-muted/50 transition-colors"
                  onClick={() => onNavigateToReader && onNavigateToReader(reading.workId, reading.chapterNumber)}
                >
                  <Circle size={20} className="text-muted-foreground" />
                  <span className="font-medium flex-1" style={{ fontFamily: 'var(--font-body)' }}>
                    {getBookDisplayName(reading.workId)} {reading.chapterNumber}
                  </span>
                  <BookOpen size={18} className="text-muted-foreground" />
                </div>
              ))}
              <div className="grid grid-cols-2 gap-3 mt-4">
                {onNavigateToReader && currentDayReading.readings.length > 0 && (
                  <Button 
                    onClick={openTodaysReading}
                    variant="secondary"
                    className="w-full"
                  >
                    <BookOpen size={20} className="mr-2" />
                    Open in Reader
                  </Button>
                )}
                <Button 
                  onClick={() => markDayComplete(currentDayReading.day)}
                  className={onNavigateToReader ? "w-full" : "w-full col-span-2"}
                  disabled={selectedUserPlan.completedDays.includes(currentDayReading.day)}
                >
                  {selectedUserPlan.completedDays.includes(currentDayReading.day) ? (
                    <>
                      <CheckCircle size={20} weight="fill" className="mr-2" />
                      Completed
                    </>
                  ) : (
                    <>
                      <CheckCircle size={20} className="mr-2" />
                      Mark Complete
                    </>
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>All Days</CardTitle>
          <CardDescription>Track your progress through the entire plan</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="list">
            <TabsList className="mb-4">
              <TabsTrigger value="list">List View</TabsTrigger>
              <TabsTrigger value="calendar">Calendar View</TabsTrigger>
            </TabsList>
            
            <TabsContent value="list">
              <ScrollArea className="h-[600px] pr-4">
                <div className="space-y-2">
                  {selectedPlan.days.map((day) => {
                    const isCompleted = selectedUserPlan.completedDays.includes(day.day)
                    const isCurrent = day.day === currentDayReading?.day
                    
                    return (
                      <div 
                        key={day.day}
                        className={`border rounded-lg p-4 transition-colors ${
                          isCurrent ? 'border-accent bg-accent/5' : ''
                        } ${isCompleted ? 'bg-muted/30' : ''}`}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-3">
                            {isCompleted ? (
                              <CheckCircle size={24} weight="fill" className="text-accent" />
                            ) : (
                              <Circle size={24} className="text-muted-foreground" />
                            )}
                            <div>
                              <h3 className="font-semibold">Day {day.day}</h3>
                              {isCurrent && <Badge variant="outline" className="mt-1">Today</Badge>}
                            </div>
                          </div>
                          <Button
                            size="sm"
                            variant={isCompleted ? 'secondary' : 'default'}
                            onClick={() => markDayComplete(day.day)}
                          >
                            {isCompleted ? 'Undo' : 'Complete'}
                          </Button>
                        </div>
                        <div className="ml-9 space-y-1">
                          {day.readings.map((reading, idx) => (
                            <div key={idx} className="text-sm text-muted-foreground">
                              • {getBookDisplayName(reading.workId)} {reading.chapterNumber}
                            </div>
                          ))}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </ScrollArea>
            </TabsContent>
            
            <TabsContent value="calendar">
              <div className="grid grid-cols-7 gap-2">
                {selectedPlan.days.map((day) => {
                  const isCompleted = selectedUserPlan.completedDays.includes(day.day)
                  const isCurrent = day.day === currentDayReading?.day
                  
                  return (
                    <button
                      key={day.day}
                      onClick={() => markDayComplete(day.day)}
                      className={`aspect-square p-2 rounded-lg border transition-all hover:border-accent ${
                        isCompleted ? 'bg-accent/20 border-accent' : 'bg-muted/20'
                      } ${isCurrent ? 'ring-2 ring-accent' : ''}`}
                    >
                      <div className="flex flex-col items-center justify-center h-full">
                        <span className="text-xs font-medium mb-1">{day.day}</span>
                        {isCompleted && <CheckCircle size={16} weight="fill" className="text-accent" />}
                      </div>
                    </button>
                  )
                })}
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      <CustomPlanBuilder
        open={showCustomPlanBuilder}
        onClose={() => setShowCustomPlanBuilder(false)}
        onCreatePlan={handleCreateCustomPlan}
      />
      </div>
    </>
  )
}
