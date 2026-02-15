import { useState } from 'react'
import { useKV } from '@/lib/local-storage-kv'
import { SavedCitation, CitationCollection, Section, Document, Jurisdiction } from '@/lib/types'
import { TagManager } from '@/components/tag-manager'
import { SmartTagSuggestions } from '@/components/smart-tag-suggestions'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Checkbox } from '@/components/ui/checkbox'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { BookmarkSimple, Plus, Tag, X } from '@phosphor-icons/react'
import { toast } from 'sonner'

interface AddToCitationLibraryDialogProps {
  open: boolean
  onClose: () => void
  section: Section
  document: Document
  jurisdiction: Jurisdiction
}

export function AddToCitationLibraryDialog({
  open,
  onClose,
  section,
  document,
  jurisdiction,
}: AddToCitationLibraryDialogProps) {
  const [savedCitations, setSavedCitations] = useKV<SavedCitation[]>('citation-library', [])
  const [collections, setCollections] = useKV<CitationCollection[]>('citation-collections', [])
  const [tagDefinitions] = useKV<any[]>('tag-definitions', [])
  const [notes, setNotes] = useState('')
  const [tags, setTags] = useState<string[]>([])
  const [selectedCollections, setSelectedCollections] = useState<string[]>([])
  const [isFavorite, setIsFavorite] = useState(false)
  const [showTagManager, setShowTagManager] = useState(false)

  const existingCitation = (savedCitations || []).find((c) => c.sectionId === section.id)

  const getTagColor = (tagName: string): string => {
    const tagDef = Array.isArray(tagDefinitions) 
      ? tagDefinitions.find((t: any) => t.name === tagName)
      : undefined
    return tagDef?.color || '#64748B'
  }

  const handleSave = () => {
    if (existingCitation) {
      setSavedCitations((current) =>
        (current || []).map((c) =>
          c.id === existingCitation.id
            ? {
                ...c,
                notes: notes || c.notes,
                tags: tags.length > 0 ? tags : c.tags,
                collections: selectedCollections,
                isFavorite: isFavorite || c.isFavorite,
                updatedAt: new Date().toISOString(),
              }
            : c
        )
      )
      toast.success('Citation updated in library')
    } else {
      const newCitation: SavedCitation = {
        id: `citation-${Date.now()}`,
        sectionId: section.id,
        documentId: document.id,
        jurisdictionId: jurisdiction.id,
        title: section.title,
        canonicalCitation: section.canonicalCitation,
        tags: tags,
        notes: notes,
        collections: selectedCollections,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        accessCount: 0,
        isFavorite: isFavorite,
      }

      setSavedCitations((current) => [newCitation, ...(current || [])])
      toast.success('Citation added to library')
    }

    setNotes('')
    setTags([])
    setSelectedCollections([])
    setIsFavorite(false)
    onClose()
  }

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(current => current.filter(t => t !== tagToRemove))
  }

  const handleToggleCollection = (collectionId: string) => {
    setSelectedCollections((current) =>
      current.includes(collectionId)
        ? current.filter((id) => id !== collectionId)
        : [...current, collectionId]
    )
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <BookmarkSimple className="w-5 h-5" />
            {existingCitation ? 'Update Citation in Library' : 'Add to Citation Library'}
          </DialogTitle>
          <DialogDescription>
            {existingCitation
              ? 'Update notes, tags, and collections for this citation'
              : 'Save this citation for quick access and organization'}
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="max-h-[calc(90vh-180px)] pr-4">
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Citation</Label>
              <div className="bg-muted p-3 rounded-lg border border-border">
                <div className="font-semibold text-sm mb-1">{section.title}</div>
                <div className="font-mono text-xs text-muted-foreground">
                  {section.canonicalCitation}
                </div>
              </div>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Badge variant="secondary">{document.type}</Badge>
                <span>•</span>
                <span>{jurisdiction.name}</span>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="notes">Notes (Optional)</Label>
              <Textarea
                id="notes"
                placeholder="Add notes about why this citation is useful, how it relates to your work, etc."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={4}
              />
            </div>

            <SmartTagSuggestions
              citation={{
                id: existingCitation?.id || '',
                sectionId: section.id,
                documentId: document.id,
                jurisdictionId: jurisdiction.id,
                title: section.title,
                canonicalCitation: section.canonicalCitation,
                tags: tags,
                notes: notes,
                collections: selectedCollections,
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString(),
                accessCount: 0,
                isFavorite: isFavorite,
              }}
              section={section}
              document={document}
              allTags={tagDefinitions || []}
              currentTags={tags}
              onApplySuggestion={(tagName) => {
                if (!tags.includes(tagName)) {
                  setTags(current => [...current, tagName])
                }
              }}
              onDismissSuggestion={() => {}}
            />

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="tags">Tags (Optional)</Label>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowTagManager(true)}
                >
                  <Tag className="w-4 h-4 mr-1" />
                  Browse Tags
                </Button>
              </div>
              {tags.length > 0 && (
                <div className="flex flex-wrap gap-2 p-2 bg-muted/50 rounded border">
                  {tags.map((tag) => (
                    <Badge
                      key={tag}
                      variant="default"
                      className="pl-2 pr-1 gap-1"
                      style={{ 
                        backgroundColor: getTagColor(tag),
                        color: 'white'
                      }}
                    >
                      {tag}
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-4 w-4 hover:bg-white/20"
                        onClick={() => handleRemoveTag(tag)}
                      >
                        <X className="w-3 h-3" />
                      </Button>
                    </Badge>
                  ))}
                </div>
              )}
              <Input
                id="tags"
                placeholder="Type tags separated by commas or click 'Browse Tags'"
                value={tags.join(', ')}
                onChange={(e) => setTags(
                  e.target.value
                    .split(',')
                    .map((t) => t.trim())
                    .filter((t) => t)
                )}
              />
              <p className="text-xs text-muted-foreground">
                Organize by topic (e.g., Commerce Clause), case type, or practice area
              </p>
            </div>

            {(collections || []).length > 0 && (
              <div className="space-y-2">
                <Label>Add to Collections</Label>
                <ScrollArea className="h-32 rounded-lg border border-border p-3">
                  <div className="space-y-2">
                    {(collections || []).map((collection) => (
                      <div key={collection.id} className="flex items-center gap-2">
                        <Checkbox
                          id={`collection-${collection.id}`}
                          checked={selectedCollections.includes(collection.id)}
                          onCheckedChange={() => handleToggleCollection(collection.id)}
                        />
                        <label
                          htmlFor={`collection-${collection.id}`}
                          className="flex items-center gap-2 flex-1 cursor-pointer"
                        >
                          <div
                            className="w-2 h-2 rounded-full"
                            style={{ backgroundColor: collection.color }}
                          />
                          <span className="text-sm">{collection.name}</span>
                          {collection.description && (
                            <span className="text-xs text-muted-foreground">
                              — {collection.description}
                            </span>
                          )}
                        </label>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </div>
            )}

            <div className="flex items-center gap-2">
              <Checkbox
                id="favorite"
                checked={isFavorite}
                onCheckedChange={(checked) => setIsFavorite(checked as boolean)}
              />
              <label htmlFor="favorite" className="text-sm cursor-pointer">
                Mark as favorite for quick access
              </label>
            </div>
          </div>
        </ScrollArea>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSave}>
            {existingCitation ? 'Update Citation' : 'Add to Library'}
          </Button>
        </DialogFooter>
      </DialogContent>

      <TagManager
        open={showTagManager}
        onClose={() => setShowTagManager(false)}
        selectedTags={tags}
        onTagsChange={setTags}
        showManagement={false}
      />
    </Dialog>
  )
}
