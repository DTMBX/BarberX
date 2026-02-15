import { useState } from 'react'
import { Warning, Scales, ShieldStar, ArrowSquareOut } from '@phosphor-icons/react'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { DisclaimerViewer } from '@/components/disclaimer-viewer'

interface SiteFooterProps {
  userId?: string
}

export function SiteFooter({ userId }: SiteFooterProps) {
  const [showFullTerms, setShowFullTerms] = useState(false)
  const currentYear = new Date().getFullYear()

  return (
    <>
      <footer className="bg-card border-t border-border print:break-before-page mt-auto">
        {/* ── Primary legal bar ───────────────────────────── */}
        <div className="bg-destructive/5 dark:bg-destructive/10 border-b border-destructive/20 dark:border-destructive/15">
          <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 py-2.5">
            <div className="flex items-start gap-3">
              <Warning className="w-5 h-5 text-destructive shrink-0 mt-0.5" weight="fill" />
              <div className="flex-1 min-w-0">
                <p className="text-[13px] font-bold text-destructive tracking-tight">
                  NOT LEGAL ADVICE — EDUCATIONAL PURPOSE ONLY
                </p>
                <p className="text-[11px] text-foreground/70 dark:text-foreground/60 leading-relaxed mt-0.5">
                  This platform provides educational information about U.S. law and constitutional principles.
                  It does not constitute legal advice, does not create an attorney-client relationship,
                  and should not be relied upon for any legal purpose. Consult a licensed attorney for legal guidance.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* ── Terms grid ────────────────────────────────────────── */}
        <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 py-5">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-x-6 gap-y-3 text-[11px] text-muted-foreground leading-relaxed">
            <div className="space-y-1">
              <h4 className="font-semibold text-foreground/80 dark:text-foreground/70 flex items-center gap-1 uppercase tracking-wider text-[10px]">
                <Scales className="w-3 h-3" weight="fill" />
                No Attorney-Client Relationship
              </h4>
              <p>
                Use of this application does not create an attorney-client relationship. 
                The creators are not your attorneys. Do not submit confidential information.
              </p>
            </div>

            <div className="space-y-1">
              <h4 className="font-semibold text-foreground/80 dark:text-foreground/70 flex items-center gap-1 uppercase tracking-wider text-[10px]">
                <ShieldStar className="w-3 h-3" weight="fill" />
                Verify All Sources
              </h4>
              <p>
                Users must verify all information through official government sources. Laws and 
                regulations change. This platform may contain errors or outdated information.
              </p>
            </div>

            <div className="space-y-1">
              <h4 className="font-semibold text-foreground/80 dark:text-foreground/70 flex items-center gap-1 uppercase tracking-wider text-[10px]">
                <Warning className="w-3 h-3" weight="fill" />
                Accuracy & Liability
              </h4>
              <p>
                We disclaim all warranties of accuracy, completeness, or fitness for purpose.
                Not admissible as legal authority. For court filings, cite official government publications.
              </p>
            </div>
          </div>

          <Separator className="my-4" />

          {/* ── Bottom bar ───────────────────────────────────────── */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-muted-foreground">
            <div className="flex items-center gap-2">
              <span className="font-serif font-semibold text-foreground/60">Civics Stack</span>
              <span className="text-foreground/30">|</span>
              <span>&copy; {currentYear} Educational Platform</span>
            </div>

            <div className="flex items-center gap-3 flex-wrap justify-center">
              <Button
                variant="link"
                size="sm"
                onClick={() => setShowFullTerms(true)}
                className="h-auto p-0 text-xs text-muted-foreground hover:text-primary underline-offset-4"
              >
                Full Terms & Disclaimers
                <ArrowSquareOut className="w-3 h-3 ml-1" />
              </Button>
              <span className="text-foreground/20 hidden sm:inline">|</span>
              <span className="text-[10px] opacity-60">
                By using this site you agree to these terms
              </span>
            </div>
          </div>
        </div>
      </footer>

      <DisclaimerViewer
        open={showFullTerms}
        onOpenChange={setShowFullTerms}
        userId={userId}
      />
    </>
  )
}
