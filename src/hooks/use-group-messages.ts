import { useKV } from '@github/spark/hooks'
import type { GroupMessage, GroupDiscussion } from '@/lib/types'

export function useGroupMessages(groups: GroupDiscussion[]): Record<string, GroupMessage[]> {
  const allMessages: Record<string, GroupMessage[]> = {}
  
  groups.forEach(group => {
    const [messages = []] = useKV<GroupMessage[]>(`group-messages-${group.id}`, [])
    allMessages[group.id] = messages
  })
  
  return allMessages
}
