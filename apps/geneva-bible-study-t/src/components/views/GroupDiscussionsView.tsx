import { useState, useEffect, useMemo } from 'react'
import { useKV } from '@github/spark/hooks'
import GroupDiscussionsList from '@/components/social/GroupDiscussionsList'
import GroupDiscussionThread from '@/components/social/GroupDiscussionThread'
import { UsersThree } from '@phosphor-icons/react'
import { useIsMobile } from '@/hooks/use-mobile'
import type { GroupDiscussion } from '@/lib/types'

export default function GroupDiscussionsView() {
  const [selectedGroup, setSelectedGroup] = useState<{
    groupId: string
    groupName: string
  } | null>(null)
  const [groups = []] = useKV<GroupDiscussion[]>('group-discussions', [])
  const isMobile = useIsMobile()

  const handleSelectGroup = (groupId: string, groupName: string) => {
    setSelectedGroup({ groupId, groupName })
  }

  const handleBack = () => {
    setSelectedGroup(null)
  }

  if (isMobile) {
    return (
      <div className="h-full">
        {selectedGroup ? (
          <GroupDiscussionThread
            groupId={selectedGroup.groupId}
            groupName={selectedGroup.groupName}
            onBack={handleBack}
          />
        ) : (
          <GroupDiscussionsList onSelectGroup={handleSelectGroup} />
        )}
      </div>
    )
  }

  return (
    <div className="h-full flex bg-background">
      <div className="w-80 border-r">
        <GroupDiscussionsList onSelectGroup={handleSelectGroup} />
      </div>
      <div className="flex-1">
        {selectedGroup ? (
          <GroupDiscussionThread
            groupId={selectedGroup.groupId}
            groupName={selectedGroup.groupName}
            onBack={handleBack}
          />
        ) : (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <UsersThree size={80} weight="duotone" className="text-muted-foreground mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Select a group discussion</h3>
              <p className="text-muted-foreground max-w-sm">
                Choose a group from the list to join Bible study discussions with multiple friends
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
