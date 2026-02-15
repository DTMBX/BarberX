import { useState, useEffect, useRef, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { Warning, SealCheck, ArrowRight, ArrowLeft, DownloadSimple } from '@phosphor-icons/react'
import { LEGAL_DISCLAIMERS, DisclaimerType, recordUserAcknowledgment } from '@/lib/compliance'
import {
  generateDisclaimerDocument,
  downloadDisclaimer,
} from '@/lib/disclaimer-export'
import { toast } from 'sonner'

interface LegalDisclaimerModalProps {
  open: boolean
  onAccept: () => void
  userId: string
}

const REQUIRED_DISCLAIMERS: DisclaimerType[] = [
  'not-legal-advice',
  'educational-only',
  'no-attorney-client',
  'verify-sources',
  'accuracy-limitation',
]

export function LegalDisclaimerModal({ open, onAccept, userId }: LegalDisclaimerModalProps) {
  const [currentPage, setCurrentPage] = useState(0)
  const [checkedDisclaimers, setCheckedDisclaimers] = useState<Set<DisclaimerType>>(new Set())
  const [isProcessing, setIsProcessing] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  const currentDisclaimerType = REQUIRED_DISCLAIMERS[currentPage]
  const currentDisclaimer = LEGAL_DISCLAIMERS[currentDisclaimerType]
  const isCurrentChecked = checkedDisclaimers.has(currentDisclaimerType)
  const isLastPage = currentPage === REQUIRED_DISCLAIMERS.length - 1
  const allChecked = REQUIRED_DISCLAIMERS.every(d => checkedDisclaimers.has(d))
  const progressPercentage = (checkedDisclaimers.size / REQUIRED_DISCLAIMERS.length) * 100

  // Scroll content to top when page changes
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: 0 })
  }, [currentPage])

  const handleCheckboxChange = useCallback(
    (checked: boolean) => {
      setCheckedDisclaimers(prev => {
        const next = new Set(prev)
        if (checked) {
          next.add(currentDisclaimerType)
        } else {
          next.delete(currentDisclaimerType)
        }
        return next
      })
    },
    [currentDisclaimerType]
  )

  const handleNext = useCallback(() => {
    if (currentPage < REQUIRED_DISCLAIMERS.length - 1) {
      setCurrentPage(p => p + 1)
    }
  }, [currentPage])

  const handleBack = useCallback(() => {
    if (currentPage > 0) {
      setCurrentPage(p => p - 1)
    }
  }, [currentPage])

  const handleAccept = async () => {
    if (!allChecked) return
    setIsProcessing(true)
    try {
      for (const dt of REQUIRED_DISCLAIMERS) {
        await recordUserAcknowledgment(userId, dt)
      }
      onAccept()
    } catch (error) {
      console.error('Error recording acknowledgments:', error)
      toast.error('Failed to save acknowledgments. Please try again.')
    } finally {
      setIsProcessing(false)
    }
  }

  // ── Safe export helper ─────────────────────────────────────────────────
  const safeGetUser = async () => {
    try {
      return await window.spark?.user?.()
    } catch {
      return null
    }
  }

  const handleExport = async (format: 'html' | 'markdown' | 'text') => {
    try {
      const user = await safeGetUser()
      const content = generateDisclaimerDocument(REQUIRED_DISCLAIMERS, {
        format,
        includeMetadata: true,
        includeTimestamp: true,
        userId,
        userName: user?.login,
      })
      downloadDisclaimer(content, format)
      toast.success(`Disclaimers exported as ${format.toUpperCase()}`)
    } catch (error) {
      toast.error('Failed to export disclaimers')
      console.error('Export error:', error)
    }
  }

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-3 sm:p-6">
      <div className="bg-background border rounded-xl shadow-2xl w-full max-w-2xl flex flex-col overflow-hidden" style={{ maxHeight: 'min(92vh, 720px)' }}>
            {/* ── Header ──────────────────────────────────────────── */}
            <div className="px-5 pt-5 pb-4 border-b bg-card shrink-0">
              <div className="flex items-start gap-3">
                <div className="flex items-center justify-center w-10 h-10 bg-destructive/10 dark:bg-destructive/20 rounded-lg shrink-0 mt-0.5">
                  <Warning className="w-5 h-5 text-destructive dark:text-destructive" weight="fill" />
                </div>
                <div className="flex-1 min-w-0">
                  <h2 className="text-lg sm:text-xl font-serif font-semibold tracking-tight">
                    Important Legal Information
                  </h2>
                  <p id="disclaimer-desc" className="text-sm text-muted-foreground mt-0.5">
                    Please review each disclosure before continuing
                  </p>
                </div>
              </div>

              {/* Progress */}
              <div className="mt-4 space-y-1.5">
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>
                    Disclosure {currentPage + 1} of {REQUIRED_DISCLAIMERS.length}
                  </span>
                  <span className="font-medium">
                    {checkedDisclaimers.size} / {REQUIRED_DISCLAIMERS.length} acknowledged
                  </span>
                </div>
                <Progress value={progressPercentage} className="h-1.5" />

                {/* Page dots for quick navigation */}
                <div className="flex items-center gap-1.5 pt-1">
                  {REQUIRED_DISCLAIMERS.map((dt, i) => (
                    <button
                      key={dt}
                      onClick={() => setCurrentPage(i)}
                      aria-label={`Go to disclosure ${i + 1}: ${LEGAL_DISCLAIMERS[dt].title}`}
                      className={`h-2 rounded-full transition-all duration-200 focus-visible:outline-2 focus-visible:outline-primary ${
                        i === currentPage
                          ? 'w-6 bg-primary'
                          : checkedDisclaimers.has(dt)
                            ? 'w-2 bg-primary/50'
                            : 'w-2 bg-muted-foreground/25'
                      }`}
                    />
                  ))}
                </div>
              </div>
            </div>

            {/* ── Scrollable Content ─────────────────────────────── */}
            <div
              ref={scrollRef}
              className="flex-1 overflow-y-auto overscroll-contain px-5 py-4 min-h-0"
            >
              <div
                className={`border-2 rounded-lg p-4 sm:p-6 transition-colors duration-200 ${
                  isCurrentChecked
                    ? 'border-primary/40 bg-primary/5'
                    : 'border-border bg-card'
                }`}
              >
                <h3 className="font-bold text-base sm:text-lg font-serif flex items-center gap-2 flex-wrap">
                  {currentDisclaimer.title}
                  {isCurrentChecked && (
                    <SealCheck className="w-5 h-5 text-primary shrink-0" weight="fill" />
                  )}
                </h3>

                <div className="mt-3 text-sm sm:text-[15px] text-foreground/90 leading-relaxed whitespace-pre-line">
                  {currentDisclaimer.content}
                </div>

                {/* Metadata */}
                <div className="mt-4 pt-3 border-t text-xs text-muted-foreground flex flex-wrap gap-x-4 gap-y-1">
                  <span>ID: {currentDisclaimer.id}</span>
                  <span>v{currentDisclaimer.version}</span>
                  <span>Effective: {currentDisclaimer.effectiveDate}</span>
                </div>
              </div>

              {/* Acknowledgment checkbox */}
              <label
                htmlFor={`ack-${currentDisclaimerType}`}
                className="flex items-start gap-3 mt-4 p-3 rounded-lg bg-muted/50 border cursor-pointer hover:bg-muted/70 transition-colors"
              >
                <Checkbox
                  id={`ack-${currentDisclaimerType}`}
                  checked={isCurrentChecked}
                  onCheckedChange={checked => handleCheckboxChange(checked as boolean)}
                  className="mt-0.5 h-5 w-5 shrink-0"
                />
                <span className="text-sm leading-relaxed select-none">
                  I have read and understand this disclosure
                </span>
              </label>
            </div>

            {/* ── Footer ─────────────────────────────────────────── */}
            <div className="px-5 py-3 border-t bg-card shrink-0">
              <div className="flex items-center justify-between gap-2">
                {/* Left: Back + Export */}
                <div className="flex items-center gap-1">
                  <Button
                    onClick={handleBack}
                    disabled={currentPage === 0}
                    variant="ghost"
                    size="sm"
                    className="gap-1.5"
                  >
                    <ArrowLeft className="w-4 h-4" />
                    <span className="hidden sm:inline">Back</span>
                  </Button>

                  <Button
                    variant="ghost"
                    size="sm"
                    className="gap-1.5 text-muted-foreground"
                    onClick={() => handleExport('text')}
                    title="Export all disclaimers as text file"
                  >
                    <DownloadSimple className="w-4 h-4" />
                    <span className="hidden sm:inline text-xs">Save</span>
                  </Button>
                </div>

                {/* Right: Next / Accept */}
                <div className="flex items-center gap-2">
                  {!isLastPage && (
                    <Button
                      onClick={handleNext}
                      disabled={!isCurrentChecked}
                      size="sm"
                      className="gap-1.5 min-w-[90px]"
                    >
                      Next
                      <ArrowRight className="w-4 h-4" />
                    </Button>
                  )}

                  {isLastPage && (
                    <Button
                      onClick={handleAccept}
                      disabled={!allChecked || isProcessing}
                      size="sm"
                      className="gap-1.5 min-w-[150px]"
                    >
                      {isProcessing ? (
                        'Processing...'
                      ) : (
                        <>
                          <SealCheck className="w-4 h-4" weight="fill" />
                          Accept & Continue
                        </>
                      )}
                    </Button>
                  )}
                </div>
              </div>

              {/* Contextual hints */}
              {!isCurrentChecked && (
                <p className="text-xs text-muted-foreground text-center mt-2">
                  Check the box above to continue
                </p>
              )}
              {isLastPage && !allChecked && isCurrentChecked && (
                <p className="text-xs text-destructive dark:text-destructive text-center mt-2">
                  You still have unacknowledged disclosures — use the dots above to review them
                </p>
              )}
            </div>
          </div>
        </div>
  )
}
