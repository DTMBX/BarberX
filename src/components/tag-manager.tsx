import { useState, useMemo, useEffect } from 'react'
import { useKV } from '@/lib/local-storage-kv'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { X, Tag, Plus, Hash, Palette, Trash } from '@phosphor-icons/react'
import { toast } from 'sonner'

export interface TagDefinition {
  id: string
  name: string
  category: TagCategory
  color: string
  description: string
  usageCount: number
  createdAt: string
}

export type TagCategory = 
  | 'constitutional-provision'
  | 'legal-topic'
  | 'case-type'
  | 'authority-level'
  | 'jurisdiction'
  | 'practice-area'
  | 'research-project'
  | 'custom'

interface TagManagerProps {
  open: boolean
  onClose: () => void
  selectedTags: string[]
  onTagsChange: (tags: string[]) => void
  showManagement?: boolean
}

const TAG_CATEGORIES: Record<TagCategory, { label: string; description: string; color: string }> = {
  'constitutional-provision': { 
    label: 'Constitutional Provision', 
    description: 'Specific constitutional clauses and amendments',
    color: '#4F46E5'
  },
  'legal-topic': { 
    label: 'Legal Topic', 
    description: 'General areas of law and legal concepts',
    color: '#059669'
  },
  'case-type': { 
    label: 'Case Type', 
    description: 'Types of legal proceedings and disputes',
    color: '#DC2626'
  },
  'authority-level': { 
    label: 'Authority Level', 
    description: 'Federal, state, or local government level',
    color: '#7C3AED'
  },
  'jurisdiction': { 
    label: 'Jurisdiction', 
    description: 'Specific geographic or subject-matter jurisdictions',
    color: '#0891B2'
  },
  'practice-area': { 
    label: 'Practice Area', 
    description: 'Legal practice specializations',
    color: '#D97706'
  },
  'research-project': { 
    label: 'Research Project', 
    description: 'Personal research initiatives and projects',
    color: '#DB2777'
  },
  'custom': { 
    label: 'Custom', 
    description: 'User-defined tags',
    color: '#64748B'
  },
}

const PREDEFINED_TAGS: Omit<TagDefinition, 'id' | 'usageCount' | 'createdAt'>[] = [
  { name: 'Commerce Clause', category: 'constitutional-provision', color: '#4F46E5', description: 'U.S. Const. art. I, § 8, cl. 3' },
  { name: 'Due Process', category: 'constitutional-provision', color: '#4F46E5', description: '5th and 14th Amendments' },
  { name: 'Equal Protection', category: 'constitutional-provision', color: '#4F46E5', description: '14th Amendment' },
  { name: 'First Amendment', category: 'constitutional-provision', color: '#4F46E5', description: 'Freedom of speech, religion, press' },
  { name: 'Supremacy Clause', category: 'constitutional-provision', color: '#4F46E5', description: 'U.S. Const. art. VI, cl. 2' },
  { name: 'Tenth Amendment', category: 'constitutional-provision', color: '#4F46E5', description: 'Reserved powers to states' },
  { name: 'Necessary and Proper', category: 'constitutional-provision', color: '#4F46E5', description: 'U.S. Const. art. I, § 8, cl. 18' },
  
  { name: 'Federalism', category: 'legal-topic', color: '#059669', description: 'Division of power between federal and state' },
  { name: 'Preemption', category: 'legal-topic', color: '#059669', description: 'Federal law superseding state law' },
  { name: 'Separation of Powers', category: 'legal-topic', color: '#059669', description: 'Division among branches of government' },
  { name: 'Statutory Interpretation', category: 'legal-topic', color: '#059669', description: 'Methods of construing legislation' },
  { name: 'Administrative Law', category: 'legal-topic', color: '#059669', description: 'Agency regulations and procedures' },
  { name: 'Civil Rights', category: 'legal-topic', color: '#059669', description: 'Constitutional rights and protections' },
  { name: 'Criminal Law', category: 'legal-topic', color: '#059669', description: 'Crimes and criminal procedures' },
  { name: 'Constitutional Law', category: 'legal-topic', color: '#059669', description: 'Interpretation and application of constitutions' },
  
  { name: 'Civil Litigation', category: 'case-type', color: '#DC2626', description: 'Private disputes between parties' },
  { name: 'Constitutional Challenge', category: 'case-type', color: '#DC2626', description: 'Challenges to law validity' },
  { name: 'Preemption Dispute', category: 'case-type', color: '#DC2626', description: 'Conflicts between authority levels' },
  { name: 'Administrative Appeal', category: 'case-type', color: '#DC2626', description: 'Appeals of agency decisions' },
  { name: 'Criminal Prosecution', category: 'case-type', color: '#DC2626', description: 'State or federal criminal cases' },
  { name: 'Injunctive Relief', category: 'case-type', color: '#DC2626', description: 'Seeking court orders to prevent harm' },
  
  { name: 'Federal', category: 'authority-level', color: '#7C3AED', description: 'U.S. Constitution and federal law' },
  { name: 'State', category: 'authority-level', color: '#7C3AED', description: 'State constitutions and statutes' },
  { name: 'Local', category: 'authority-level', color: '#7C3AED', description: 'Municipal ordinances and county rules' },
  { name: 'Treaty', category: 'authority-level', color: '#7C3AED', description: 'International agreements' },
  
  { name: 'Immigration', category: 'practice-area', color: '#D97706', description: 'Immigration and naturalization law' },
  { name: 'Environmental', category: 'practice-area', color: '#D97706', description: 'Environmental regulations' },
  { name: 'Employment', category: 'practice-area', color: '#D97706', description: 'Labor and employment law' },
  { name: 'Education', category: 'practice-area', color: '#D97706', description: 'Educational institutions and rights' },
  { name: 'Healthcare', category: 'practice-area', color: '#D97706', description: 'Medical and health regulations' },
  { name: 'Housing', category: 'practice-area', color: '#D97706', description: 'Landlord-tenant and housing law' },
]

export function TagManager({ open, onClose, selectedTags, onTagsChange, showManagement = true }: TagManagerProps) {
  const [tagDefinitions, setTagDefinitions] = useKV<TagDefinition[]>('tag-definitions', [])
  const [searchQuery, setSearchQuery] = useState('')
  const [filterCategory, setFilterCategory] = useState<TagCategory | 'all'>('all')
  const [showNewTag, setShowNewTag] = useState(false)
  const [newTagName, setNewTagName] = useState('')
  const [newTagCategory, setNewTagCategory] = useState<TagCategory>('custom')
  const [newTagDescription, setNewTagDescription] = useState('')

  const initializePredefinedTags = () => {
    const existing = tagDefinitions || []
    const existingNames = new Set(existing.map(t => t.name.toLowerCase()))
    
    const newTags = PREDEFINED_TAGS
      .filter(pt => !existingNames.has(pt.name.toLowerCase()))
      .map((pt, idx) => ({
        ...pt,
        id: `tag-${Date.now()}-${idx}`,
        usageCount: 0,
        createdAt: new Date().toISOString(),
      }))
    
    if (newTags.length > 0) {
      setTagDefinitions(current => [...(current || []), ...newTags])
      toast.success(`Added ${newTags.length} predefined tags`)
    }
  }

  useEffect(() => {
    if ((tagDefinitions || []).length === 0) {
      initializePredefinedTags()
    }
  }, [])

  const allTags = useMemo(() => {
    return tagDefinitions || []
  }, [tagDefinitions])

  const filteredTags = useMemo(() => {
    let filtered = allTags

    if (filterCategory !== 'all') {
      filtered = filtered.filter(t => t.category === filterCategory)
    }

    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(
        t => t.name.toLowerCase().includes(query) || 
             t.description.toLowerCase().includes(query)
      )
    }

    return filtered.sort((a, b) => {
      const aSelected = selectedTags.includes(a.name)
      const bSelected = selectedTags.includes(b.name)
      if (aSelected && !bSelected) return -1
      if (!aSelected && bSelected) return 1
      return b.usageCount - a.usageCount
    })
  }, [allTags, searchQuery, filterCategory, selectedTags])

  const tagsByCategory = useMemo(() => {
    const grouped: Record<TagCategory, TagDefinition[]> = {
      'constitutional-provision': [],
      'legal-topic': [],
      'case-type': [],
      'authority-level': [],
      'jurisdiction': [],
      'practice-area': [],
      'research-project': [],
      'custom': [],
    }

    filteredTags.forEach(tag => {
      grouped[tag.category].push(tag)
    })

    return grouped
  }, [filteredTags])

  const handleToggleTag = (tagName: string) => {
    const newTags = selectedTags.includes(tagName)
      ? selectedTags.filter(t => t !== tagName)
      : [...selectedTags, tagName]
    
    onTagsChange(newTags)

    setTagDefinitions(current =>
      (current || []).map(t =>
        t.name === tagName && !selectedTags.includes(tagName)
          ? { ...t, usageCount: t.usageCount + 1 }
          : t
      )
    )
  }

  const handleCreateTag = () => {
    if (!newTagName.trim()) {
      toast.error('Tag name is required')
      return
    }

    const existingTag = allTags.find(t => t.name.toLowerCase() === newTagName.toLowerCase())
    if (existingTag) {
      toast.error('Tag already exists')
      return
    }

    const newTag: TagDefinition = {
      id: `tag-${Date.now()}`,
      name: newTagName.trim(),
      category: newTagCategory,
      color: TAG_CATEGORIES[newTagCategory].color,
      description: newTagDescription.trim(),
      usageCount: 0,
      createdAt: new Date().toISOString(),
    }

    setTagDefinitions(current => [...(current || []), newTag])
    setNewTagName('')
    setNewTagDescription('')
    setNewTagCategory('custom')
    setShowNewTag(false)
    toast.success('Tag created')
  }

  const handleDeleteTag = (tagId: string) => {
    setTagDefinitions(current => (current || []).filter(t => t.id !== tagId))
    toast.success('Tag deleted')
  }

  const handleRemoveTag = (tagName: string) => {
    onTagsChange(selectedTags.filter(t => t !== tagName))
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Tag className="w-5 h-5" />
            Tag Manager
          </DialogTitle>
          <DialogDescription>
            Organize citations by topic, case type, or practice area
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-hidden flex flex-col gap-4">
          <div className="space-y-4">
            {selectedTags.length > 0 && (
              <div className="space-y-2">
                <Label>Selected Tags ({selectedTags.length})</Label>
                <div className="flex flex-wrap gap-2 p-3 bg-muted/50 rounded-lg border">
                  {selectedTags.map(tagName => {
                    const tagDef = allTags.find(t => t.name === tagName)
                    return (
                      <Badge
                        key={tagName}
                        variant="default"
                        className="pl-2 pr-1 gap-1"
                        style={{ 
                          backgroundColor: tagDef?.color || '#64748B',
                          color: 'white'
                        }}
                      >
                        {tagName}
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-4 w-4 hover:bg-white/20"
                          onClick={() => handleRemoveTag(tagName)}
                        >
                          <X className="w-3 h-3" />
                        </Button>
                      </Badge>
                    )
                  })}
                </div>
              </div>
            )}

            <div className="flex gap-2">
              <div className="flex-1">
                <Input
                  placeholder="Search tags..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full"
                />
              </div>
              <Select
                value={filterCategory}
                onValueChange={(value) => setFilterCategory(value as TagCategory | 'all')}
              >
                <SelectTrigger className="w-[200px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  {Object.entries(TAG_CATEGORIES).map(([key, { label }]) => (
                    <SelectItem key={key} value={key}>
                      {label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {showManagement && (
                <Button size="sm" onClick={() => setShowNewTag(true)}>
                  <Plus className="w-4 h-4 mr-1" />
                  New
                </Button>
              )}
            </div>
          </div>

          <Separator />

          <ScrollArea className="flex-1 pr-4">
            <div className="space-y-6">
              {Object.entries(TAG_CATEGORIES).map(([categoryKey, categoryInfo]) => {
                const categoryTags = tagsByCategory[categoryKey as TagCategory]
                if (categoryTags.length === 0 && filterCategory !== 'all' && filterCategory !== categoryKey) {
                  return null
                }

                return (
                  <div key={categoryKey} className="space-y-3">
                    <div className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: categoryInfo.color }}
                      />
                      <h3 className="font-semibold text-sm">{categoryInfo.label}</h3>
                      <span className="text-xs text-muted-foreground">
                        ({categoryTags.length})
                      </span>
                    </div>
                    
                    {categoryTags.length > 0 ? (
                      <div className="flex flex-wrap gap-2">
                        {categoryTags.map(tag => (
                          <Badge
                            key={tag.id}
                            variant={selectedTags.includes(tag.name) ? 'default' : 'outline'}
                            className="cursor-pointer hover:shadow-sm transition-shadow group relative pr-8"
                            style={
                              selectedTags.includes(tag.name)
                                ? { backgroundColor: tag.color, color: 'white', borderColor: tag.color }
                                : { borderColor: tag.color, color: tag.color }
                            }
                            onClick={() => handleToggleTag(tag.name)}
                          >
                            <span className="flex items-center gap-1">
                              {tag.name}
                              {tag.usageCount > 0 && (
                                <span className="text-xs opacity-70">({tag.usageCount})</span>
                              )}
                            </span>
                            {showManagement && tag.category === 'custom' && (
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-4 w-4 absolute right-1 opacity-0 group-hover:opacity-100 hover:bg-destructive/20"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  handleDeleteTag(tag.id)
                                }}
                              >
                                <Trash className="w-3 h-3" />
                              </Button>
                            )}
                          </Badge>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-muted-foreground italic">
                        No tags in this category
                      </p>
                    )}
                  </div>
                )
              })}
            </div>
          </ScrollArea>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Done
          </Button>
        </DialogFooter>
      </DialogContent>

      <Dialog open={showNewTag} onOpenChange={setShowNewTag}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Tag</DialogTitle>
            <DialogDescription>
              Add a custom tag to organize your citations
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="tag-name">Tag Name</Label>
              <Input
                id="tag-name"
                placeholder="e.g., Voting Rights"
                value={newTagName}
                onChange={(e) => setNewTagName(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="tag-category">Category</Label>
              <Select
                value={newTagCategory}
                onValueChange={(value) => setNewTagCategory(value as TagCategory)}
              >
                <SelectTrigger id="tag-category">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(TAG_CATEGORIES).map(([key, { label }]) => (
                    <SelectItem key={key} value={key}>
                      {label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="tag-description">Description (Optional)</Label>
              <Input
                id="tag-description"
                placeholder="Brief description of this tag"
                value={newTagDescription}
                onChange={(e) => setNewTagDescription(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowNewTag(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateTag}>Create Tag</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Dialog>
  )
}
