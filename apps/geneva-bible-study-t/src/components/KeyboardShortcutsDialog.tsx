import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Keyboard } from '@phosphor-icons/react'

interface KeyboardShortcutsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export default function KeyboardShortcutsDialog({ open, onOpenChange }: KeyboardShortcutsDialogProps) {
  const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0
  const modKey = isMac ? '⌘' : 'Ctrl'

  const shortcuts = [
    {
      category: 'Navigation',
      items: [
        { keys: ['1-9'], description: 'Switch to tab by number' },
        { keys: [modKey, 'K'], description: 'Open search' },
        { keys: ['Escape'], description: 'Close dialog or go back' },
        { keys: ['Tab'], description: 'Navigate forward' },
        { keys: ['Shift', 'Tab'], description: 'Navigate backward' },
      ]
    },
    {
      category: 'Reader',
      items: [
        { keys: [modKey, 'B'], description: 'Add bookmark' },
        { keys: [modKey, 'H'], description: 'Add highlight' },
        { keys: [modKey, 'N'], description: 'Add note' },
        { keys: [modKey, 'C'], description: 'Compare translations' },
        { keys: ['ArrowLeft'], description: 'Previous chapter' },
        { keys: ['ArrowRight'], description: 'Next chapter' },
      ]
    },
    {
      category: 'Audio',
      items: [
        { keys: ['Space'], description: 'Play/Pause audio' },
        { keys: [modKey, 'M'], description: 'Toggle microphone' },
        { keys: ['ArrowUp'], description: 'Increase volume' },
        { keys: ['ArrowDown'], description: 'Decrease volume' },
      ]
    },
    {
      category: 'Messages',
      items: [
        { keys: ['Enter'], description: 'Send message' },
        { keys: ['Shift', 'Enter'], description: 'New line' },
        { keys: [modKey, 'M'], description: 'Start voice message' },
        { keys: [modKey, 'E'], description: 'Edit last message' },
      ]
    },
    {
      category: 'General',
      items: [
        { keys: [modKey, 'D'], description: 'Toggle dark mode' },
        { keys: [modKey, 'S'], description: 'Save/Submit' },
        { keys: [modKey, ','], description: 'Open settings' },
        { keys: [modKey, '/'], description: 'Show keyboard shortcuts' },
        { keys: ['?'], description: 'Show help' },
      ]
    }
  ]

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Keyboard size={24} weight="duotone" className="text-primary" />
            Keyboard Shortcuts
          </DialogTitle>
          <DialogDescription>
            Use these shortcuts to navigate the app more efficiently
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {shortcuts.map((section, idx) => (
            <div key={section.category}>
              {idx > 0 && <Separator />}
              <div className="space-y-3">
                <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wide">
                  {section.category}
                </h3>
                <div className="space-y-2">
                  {section.items.map((shortcut, itemIdx) => (
                    <Card key={itemIdx} className="p-3 flex items-center justify-between hover:bg-muted/50 transition-colors">
                      <span className="text-sm">{shortcut.description}</span>
                      <div className="flex items-center gap-1">
                        {shortcut.keys.map((key, keyIdx) => (
                          <Badge
                            key={keyIdx}
                            variant="secondary"
                            className="font-mono text-xs px-2 py-1"
                          >
                            {key}
                          </Badge>
                        ))}
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 p-3 bg-muted/50 rounded-md">
          <p className="text-xs text-muted-foreground">
            <strong>Tip:</strong> Most keyboard shortcuts work globally throughout the app.
            Press <Badge variant="secondary" className="inline-flex mx-1 text-xs">{modKey} + /</Badge> 
            anytime to view this dialog.
          </p>
        </div>
      </DialogContent>
    </Dialog>
  )
}
