import { useState } from 'react'
import { useKV } from '@/lib/local-storage-kv'
import { LocalSubmission } from '@/lib/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { toast } from 'sonner'
import { Upload, FileText, CheckCircle, Clock, Warning, Trash, Eye } from '@phosphor-icons/react'
import { jurisdictions } from '@/lib/seed-data'

export function LocalOrdinanceSubmission() {
  const [submissions, setSubmissions] = useKV<LocalSubmission[]>('local-submissions', [])
  const [showSubmitForm, setShowSubmitForm] = useState(false)
  const [viewingSubmission, setViewingSubmission] = useState<LocalSubmission | null>(null)

  const [formData, setFormData] = useState({
    documentTitle: '',
    jurisdictionId: '',
    sourceUrl: '',
    description: '',
    verificationProof: ''
  })

  const handleSubmit = async () => {
    if (!formData.documentTitle || !formData.jurisdictionId || !formData.sourceUrl) {
      toast.error('Please fill in all required fields')
      return
    }

    const user = await window.spark.user().catch(() => null)

    const newSubmission: LocalSubmission = {
      id: `submission-${Date.now()}`,
      documentTitle: formData.documentTitle,
      jurisdictionId: formData.jurisdictionId,
      sourceUrl: formData.sourceUrl,
      submittedBy: user?.login || 'anonymous',
      submittedAt: new Date().toISOString(),
      verificationStatus: 'unverified',
      curatorNotes: formData.description
    }

    setSubmissions(current => [newSubmission, ...(current || [])])
    
    toast.success('Submission received', {
      description: 'Your local ordinance submission is pending verification.'
    })

    setFormData({
      documentTitle: '',
      jurisdictionId: '',
      sourceUrl: '',
      description: '',
      verificationProof: ''
    })
    setShowSubmitForm(false)
  }

  const handleDelete = (id: string) => {
    setSubmissions(current => (current || []).filter(s => s.id !== id))
    toast.success('Submission deleted')
  }

  const getStatusIcon = (status: LocalSubmission['verificationStatus']) => {
    switch (status) {
      case 'official':
        return <CheckCircle weight="fill" className="text-accent" size={20} />
      case 'verified':
        return <CheckCircle weight="fill" className="text-primary" size={20} />
      case 'unverified':
        return <Clock className="text-muted-foreground" size={20} />
      default:
        return <Warning className="text-muted-foreground" size={20} />
    }
  }

  const getStatusBadge = (status: LocalSubmission['verificationStatus']) => {
    const variants: Record<string, 'default' | 'secondary' | 'outline'> = {
      official: 'default',
      verified: 'default',
      unverified: 'secondary'
    }

    return (
      <Badge variant={variants[status] || 'outline'} className="capitalize">
        {status}
      </Badge>
    )
  }

  const localJurisdictions = jurisdictions.filter(
    j => j.type === 'county' || j.type === 'municipality'
  )

  const userSubmissions = submissions || []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold font-serif">Local Ordinance Contributions</h2>
          <p className="text-muted-foreground mt-1">
            Submit local ordinances and municipal codes for community verification
          </p>
        </div>
        <Button onClick={() => setShowSubmitForm(true)} className="gap-2">
          <Upload weight="bold" />
          Submit Ordinance
        </Button>
      </div>

      <Alert>
        <Warning weight="bold" className="h-4 w-4" />
        <AlertDescription>
          <strong>Verification Process:</strong> All submissions require verification before appearing in search results. 
          Please provide official source URLs and accurate information. Submissions must link to official government 
          sources or provide verifiable documentation.
        </AlertDescription>
      </Alert>

      {userSubmissions.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <FileText size={64} weight="thin" className="text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No submissions yet</h3>
            <p className="text-sm text-muted-foreground text-center max-w-md mb-4">
              Help build a comprehensive database of local ordinances by submitting municipal 
              codes and county regulations from your community.
            </p>
            <Button onClick={() => setShowSubmitForm(true)} variant="outline" className="gap-2">
              <Upload weight="bold" />
              Make Your First Submission
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Your Submissions</CardTitle>
            <CardDescription>
              Track the status of your local ordinance contributions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Status</TableHead>
                  <TableHead>Document Title</TableHead>
                  <TableHead>Submitted</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {userSubmissions.map(submission => {
                  const jurisdiction = jurisdictions.find(j => j.id === submission.jurisdictionId)
                  return (
                    <TableRow key={submission.id}>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {getStatusIcon(submission.verificationStatus)}
                          {getStatusBadge(submission.verificationStatus)}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <div className="font-medium">{submission.documentTitle}</div>
                          <div className="text-sm text-muted-foreground">
                            {jurisdiction?.name || submission.jurisdictionId}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {new Date(submission.submittedAt).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setViewingSubmission(submission)}
                          >
                            <Eye size={16} />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(submission.id)}
                          >
                            <Trash size={16} />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      <Dialog open={showSubmitForm} onOpenChange={setShowSubmitForm}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Submit Local Ordinance</DialogTitle>
            <DialogDescription>
              Contribute to the database by submitting local municipal codes or county ordinances. 
              All submissions require verification before being made available to the community.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="document-title">
                Document Title <span className="text-destructive">*</span>
              </Label>
              <Input
                id="document-title"
                placeholder="e.g., San Francisco Municipal Code"
                value={formData.documentTitle}
                onChange={e => setFormData({ ...formData, documentTitle: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="jurisdiction">
                Jurisdiction <span className="text-destructive">*</span>
              </Label>
              <Select
                value={formData.jurisdictionId}
                onValueChange={value => setFormData({ ...formData, jurisdictionId: value })}
              >
                <SelectTrigger id="jurisdiction">
                  <SelectValue placeholder="Select a jurisdiction" />
                </SelectTrigger>
                <SelectContent>
                  {jurisdictions
                    .filter(j => j.type !== 'federal')
                    .map(jurisdiction => (
                      <SelectItem key={jurisdiction.id} value={jurisdiction.id}>
                        {jurisdiction.name} ({jurisdiction.abbreviation})
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="source-url">
                Official Source URL <span className="text-destructive">*</span>
              </Label>
              <Input
                id="source-url"
                type="url"
                placeholder="https://..."
                value={formData.sourceUrl}
                onChange={e => setFormData({ ...formData, sourceUrl: e.target.value })}
              />
              <p className="text-xs text-muted-foreground">
                Must be from an official government website (.gov domain preferred)
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description & Notes</Label>
              <Textarea
                id="description"
                placeholder="Provide any relevant context, effective dates, or verification details..."
                value={formData.description}
                onChange={e => setFormData({ ...formData, description: e.target.value })}
                rows={4}
              />
            </div>

            <Alert>
              <Warning weight="bold" className="h-4 w-4" />
              <AlertDescription className="text-xs">
                By submitting, you confirm that this information is accurate and comes from an 
                official source. False submissions may result in loss of contributor privileges.
              </AlertDescription>
            </Alert>
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setShowSubmitForm(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmit}>
              Submit for Verification
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={!!viewingSubmission} onOpenChange={() => setViewingSubmission(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Submission Details</DialogTitle>
          </DialogHeader>

          {viewingSubmission && (
            <div className="space-y-4 py-4">
              <div>
                <Label className="text-xs text-muted-foreground">Title</Label>
                <p className="font-medium">{viewingSubmission.documentTitle}</p>
              </div>

              <div>
                <Label className="text-xs text-muted-foreground">Status</Label>
                <div className="mt-1">{getStatusBadge(viewingSubmission.verificationStatus)}</div>
              </div>

              <div>
                <Label className="text-xs text-muted-foreground">Jurisdiction</Label>
                <p>{jurisdictions.find(j => j.id === viewingSubmission.jurisdictionId)?.name}</p>
              </div>

              <div>
                <Label className="text-xs text-muted-foreground">Source URL</Label>
                <a
                  href={viewingSubmission.sourceUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-primary hover:underline block"
                >
                  {viewingSubmission.sourceUrl}
                </a>
              </div>

              <div>
                <Label className="text-xs text-muted-foreground">Submitted</Label>
                <p className="text-sm">
                  {new Date(viewingSubmission.submittedAt).toLocaleString()}
                </p>
              </div>

              {viewingSubmission.curatorNotes && (
                <div>
                  <Label className="text-xs text-muted-foreground">Notes</Label>
                  <p className="text-sm">{viewingSubmission.curatorNotes}</p>
                </div>
              )}

              {viewingSubmission.reviewedBy && (
                <div>
                  <Label className="text-xs text-muted-foreground">Reviewed By</Label>
                  <p className="text-sm">
                    {viewingSubmission.reviewedBy} on{' '}
                    {viewingSubmission.reviewedAt && new Date(viewingSubmission.reviewedAt).toLocaleDateString()}
                  </p>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
