import { useState } from 'react'
import { useKV } from '@/lib/local-storage-kv'
import { LocalSubmission, Jurisdiction } from '@/lib/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Buildings,
  Warning,
  SealCheck,
  Link as LinkIcon,
  Upload,
  CheckCircle,
  Clock,
  XCircle,
  Plus,
  ShieldWarning
} from '@phosphor-icons/react'
import { toast } from 'sonner'

interface LocalOverlayViewProps {
  jurisdiction: Jurisdiction | undefined
  onViewDocument?: (submissionId: string) => void
}

export function LocalOverlayView({ jurisdiction, onViewDocument }: LocalOverlayViewProps) {
  const [submissions, setSubmissions] = useKV<LocalSubmission[]>('local-submissions', [])
  const [showUnverified, setShowUnverified] = useState(false)
  const [isSubmitDialogOpen, setIsSubmitDialogOpen] = useState(false)

  const [formData, setFormData] = useState({
    documentTitle: '',
    sourceUrl: '',
    municipalityType: 'city',
    municipalityName: '',
    notes: ''
  })

  const filteredSubmissions = (submissions || []).filter(sub => {
    if (!jurisdiction) return true
    
    const matchesJurisdiction = sub.jurisdictionId.startsWith(jurisdiction.id)
    const matchesVerificationFilter = showUnverified || sub.verificationStatus !== 'unverified'
    
    return matchesJurisdiction && matchesVerificationFilter
  })

  const verifiedCount = filteredSubmissions.filter(s => s.verificationStatus === 'verified').length
  const officialCount = filteredSubmissions.filter(s => s.verificationStatus === 'official').length
  const unverifiedCount = filteredSubmissions.filter(s => s.verificationStatus === 'unverified').length

  const handleSubmit = async () => {
    if (!formData.documentTitle || !formData.sourceUrl || !formData.municipalityName) {
      toast.error('Please fill in all required fields')
      return
    }

    try {
      new URL(formData.sourceUrl)
    } catch {
      toast.error('Please enter a valid URL for the source')
      return
    }

    const user = await window.spark.user().catch(() => null)
    const userId = user?.login || String(user?.id) || 'anonymous'

    const newSubmission: LocalSubmission = {
      id: `local-${Date.now()}-${Math.random().toString(36).substring(2, 11)}`,  
      documentTitle: formData.documentTitle,
      jurisdictionId: jurisdiction?.id || 'us-federal',
      sourceUrl: formData.sourceUrl,
      submittedBy: userId,
      submittedAt: new Date().toISOString(),
      verificationStatus: 'unverified',
      curatorNotes: formData.notes
    }

    setSubmissions(current => [newSubmission, ...(current || [])])

    toast.success('Local ordinance submitted successfully', {
      description: 'Your submission will be reviewed by curators for verification.'
    })

    setFormData({
      documentTitle: '',
      sourceUrl: '',
      municipalityType: 'city',
      municipalityName: '',
      notes: ''
    })
    setIsSubmitDialogOpen(false)
  }

  const getStatusIcon = (status: LocalSubmission['verificationStatus']) => {
    switch (status) {
      case 'official':
        return <SealCheck weight="fill" className="text-primary" />
      case 'verified':
        return <CheckCircle weight="fill" className="text-green-600" />
      case 'unverified':
        return <Clock weight="fill" className="text-accent-foreground dark:text-accent" />
      default:
        return <XCircle weight="fill" className="text-muted-foreground" />
    }
  }

  const getStatusLabel = (status: LocalSubmission['verificationStatus']) => {
    switch (status) {
      case 'official':
        return 'Official Source'
      case 'verified':
        return 'Curator Verified'
      case 'unverified':
        return 'Pending Verification'
      default:
        return 'Unknown'
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-3 mb-2">
          <Buildings size={32} className="text-primary" weight="fill" />
          <div>
            <h1 className="text-3xl font-bold font-serif">Local Overlay</h1>
            <p className="text-muted-foreground">
              Municipal and county ordinances with verification status
            </p>
          </div>
        </div>
      </div>

      <Alert className="border-accent/30 dark:border-accent/20 bg-accent/5 dark:bg-accent/10">
        <ShieldWarning className="text-accent-foreground dark:text-accent" />
        <AlertDescription className="text-sm text-foreground/80 dark:text-foreground/70">
          <strong>Verification Standards:</strong> Local ordinances are verified by curators to ensure
          accuracy and proper sourcing. Unverified submissions are hidden by default and should not be
          relied upon for legal purposes without independent verification.
        </AlertDescription>
      </Alert>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <CardDescription className="text-xs">Total Sources</CardDescription>
            <CardTitle className="text-3xl font-bold">
              {filteredSubmissions.length}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardDescription className="text-xs flex items-center gap-1">
              <SealCheck size={14} weight="fill" />
              Official
            </CardDescription>
            <CardTitle className="text-3xl font-bold text-primary">
              {officialCount}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardDescription className="text-xs flex items-center gap-1">
              <CheckCircle size={14} weight="fill" />
              Verified
            </CardDescription>
            <CardTitle className="text-3xl font-bold text-green-600">
              {verifiedCount}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardDescription className="text-xs flex items-center gap-1">
              <Clock size={14} weight="fill" />
              Unverified
            </CardDescription>
            <CardTitle className="text-3xl font-bold text-accent-foreground dark:text-accent">
              {unverifiedCount}
            </CardTitle>
          </CardHeader>
        </Card>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Switch
              id="show-unverified"
              checked={showUnverified}
              onCheckedChange={setShowUnverified}
            />
            <Label htmlFor="show-unverified" className="cursor-pointer">
              Show unverified submissions
            </Label>
          </div>
        </div>

        <Dialog open={isSubmitDialogOpen} onOpenChange={setIsSubmitDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2" />
              Submit Local Ordinance
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Submit Local Ordinance</DialogTitle>
              <DialogDescription>
                Contribute a local ordinance or municipal code with proper source documentation
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4">
              <Alert className="border-accent/30 dark:border-accent/20 bg-accent/5 dark:bg-accent/10">
                <Warning className="text-accent-foreground dark:text-accent" />
                <AlertDescription className="text-sm text-foreground/80 dark:text-foreground/70">
                  <strong>Required:</strong> You must provide a link to an official government source.
                  Personal documents, screenshots, or unofficial summaries will not be accepted.
                </AlertDescription>
              </Alert>

              <div className="space-y-2">
                <Label htmlFor="document-title">Document Title *</Label>
                <Input
                  id="document-title"
                  placeholder="e.g., Municipal Code Chapter 12.5 - Noise Ordinance"
                  value={formData.documentTitle}
                  onChange={(e) => setFormData({ ...formData, documentTitle: e.target.value })}
                />
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="municipality-type">Jurisdiction Type *</Label>
                  <select
                    id="municipality-type"
                    className="w-full px-3 py-2 border rounded-md"
                    value={formData.municipalityType}
                    onChange={(e) => setFormData({ ...formData, municipalityType: e.target.value })}
                  >
                    <option value="city">City</option>
                    <option value="county">County</option>
                    <option value="township">Township</option>
                    <option value="village">Village</option>
                    <option value="borough">Borough</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="municipality-name">Municipality Name *</Label>
                  <Input
                    id="municipality-name"
                    placeholder="e.g., San Francisco"
                    value={formData.municipalityName}
                    onChange={(e) => setFormData({ ...formData, municipalityName: e.target.value })}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="source-url">Official Source URL *</Label>
                <div className="relative">
                  <LinkIcon className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={16} />
                  <Input
                    id="source-url"
                    type="url"
                    placeholder="https://..."
                    className="pl-9"
                    value={formData.sourceUrl}
                    onChange={(e) => setFormData({ ...formData, sourceUrl: e.target.value })}
                  />
                </div>
                <p className="text-xs text-muted-foreground">
                  Must link directly to the ordinance on an official government website
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="notes">Additional Notes (Optional)</Label>
                <Textarea
                  id="notes"
                  placeholder="Any additional context or notes for curators..."
                  rows={3}
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                />
              </div>

              <div className="flex gap-2 justify-end">
                <Button variant="outline" onClick={() => setIsSubmitDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleSubmit}>
                  <Upload className="mr-2" />
                  Submit for Review
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <ScrollArea className="h-[600px]">
        <div className="space-y-3 pr-4">
          {filteredSubmissions.length === 0 ? (
            <Card className="py-12">
              <CardContent className="text-center text-muted-foreground">
                <Buildings size={48} className="mx-auto mb-4 opacity-50" />
                <p className="text-lg font-medium">No local ordinances available</p>
                <p className="text-sm mt-2">
                  {showUnverified
                    ? 'No submissions found for this jurisdiction.'
                    : 'Enable "Show unverified submissions" to see pending items.'}
                </p>
              </CardContent>
            </Card>
          ) : (
            filteredSubmissions.map((submission) => (
              <Card
                key={submission.id}
                className={`cursor-pointer hover:border-primary/50 transition-colors ${
                  submission.verificationStatus === 'unverified' ? 'border-accent/30 bg-accent/5 dark:bg-accent/10' : ''
                }`}
                onClick={() => onViewDocument?.(submission.id)}
              >
                <CardHeader>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        {getStatusIcon(submission.verificationStatus)}
                        <Badge variant={submission.verificationStatus === 'official' ? 'default' : 'secondary'}>
                          {getStatusLabel(submission.verificationStatus)}
                        </Badge>
                      </div>
                      <CardTitle className="text-base font-serif">{submission.documentTitle}</CardTitle>
                      <CardDescription className="mt-1">
                        Submitted by {submission.submittedBy} on{' '}
                        {new Date(submission.submittedAt).toLocaleDateString()}
                      </CardDescription>
                      <div className="mt-3 flex items-center gap-2 text-sm">
                        <LinkIcon size={14} className="text-muted-foreground" />
                        <a
                          href={submission.sourceUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary hover:underline"
                          onClick={(e) => e.stopPropagation()}
                        >
                          View Official Source
                        </a>
                      </div>
                      {submission.verificationStatus === 'verified' && submission.reviewedBy && (
                        <div className="mt-2 text-xs text-muted-foreground">
                          Verified by {submission.reviewedBy} on{' '}
                          {submission.reviewedAt && new Date(submission.reviewedAt).toLocaleDateString()}
                        </div>
                      )}
                    </div>
                  </div>
                </CardHeader>
              </Card>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  )
}
