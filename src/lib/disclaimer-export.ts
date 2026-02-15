import { LEGAL_DISCLAIMERS, DisclaimerType, LegalDisclaimer } from './compliance'

export interface DisclaimerExportOptions {
  format: 'pdf' | 'text' | 'markdown' | 'html'
  includeMetadata?: boolean
  includeTimestamp?: boolean
  userId?: string
  userName?: string
}

export interface DisclaimerExportData {
  disclaimers: LegalDisclaimer[]
  exportedAt: string
  exportedBy?: string
  version: string
  purpose: string
}

export function generateDisclaimerDocument(
  disclaimerTypes: DisclaimerType[],
  options: DisclaimerExportOptions
): string {
  const disclaimers = disclaimerTypes.map((type) => LEGAL_DISCLAIMERS[type])
  const exportData: DisclaimerExportData = {
    disclaimers,
    exportedAt: new Date().toISOString(),
    exportedBy: options.userName || options.userId,
    version: '1.0',
    purpose: 'Court-Defensible Legal Disclaimer Documentation',
  }

  switch (options.format) {
    case 'html':
      return generateHTMLDocument(exportData, options)
    case 'markdown':
      return generateMarkdownDocument(exportData, options)
    case 'text':
      return generateTextDocument(exportData, options)
    case 'pdf':
      return generateHTMLForPDF(exportData, options)
    default:
      return generateTextDocument(exportData, options)
  }
}

function generateHTMLDocument(
  data: DisclaimerExportData,
  options: DisclaimerExportOptions
): string {
  const metadata = options.includeMetadata
    ? `
    <div style="background: #f3f4f6; padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 2rem;">
      <h3 style="margin: 0 0 1rem 0; color: #1f2937; font-size: 1.125rem;">Document Information</h3>
      <p style="margin: 0.25rem 0; color: #4b5563;"><strong>Exported:</strong> ${new Date(data.exportedAt).toLocaleString()}</p>
      ${data.exportedBy ? `<p style="margin: 0.25rem 0; color: #4b5563;"><strong>Exported by:</strong> ${data.exportedBy}</p>` : ''}
      <p style="margin: 0.25rem 0; color: #4b5563;"><strong>Version:</strong> ${data.version}</p>
      <p style="margin: 0.25rem 0; color: #4b5563;"><strong>Purpose:</strong> ${data.purpose}</p>
    </div>
    `
    : ''

  const disclaimerSections = data.disclaimers
    .map(
      (disclaimer, index) => `
    <section style="margin-bottom: 2.5rem; page-break-inside: avoid;">
      <div style="border-left: 4px solid #3b82f6; padding-left: 1rem; margin-bottom: 1rem;">
        <h2 style="margin: 0; color: #1f2937; font-size: 1.5rem;">${index + 1}. ${disclaimer.title}</h2>
        <p style="margin: 0.5rem 0 0 0; color: #6b7280; font-size: 0.875rem;">
          ID: ${disclaimer.id} | Type: ${disclaimer.type} | Version: ${disclaimer.version} | Effective: ${disclaimer.effectiveDate}
        </p>
      </div>
      <div style="background: #fffbeb; border: 2px solid #fbbf24; border-radius: 0.5rem; padding: 1.5rem;">
        <p style="margin: 0; color: #78350f; line-height: 1.75; white-space: pre-wrap;">${disclaimer.content}</p>
      </div>
    </section>
    `
    )
    .join('')

  return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Legal Disclaimers - Civics Stack</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      line-height: 1.6;
      color: #1f2937;
      max-width: 850px;
      margin: 0 auto;
      padding: 2rem;
      background: #ffffff;
    }
    @media print {
      body { padding: 1rem; }
      h1 { font-size: 1.75rem; }
      h2 { font-size: 1.25rem; }
    }
  </style>
</head>
<body>
  <header style="text-align: center; margin-bottom: 3rem; border-bottom: 3px solid #3b82f6; padding-bottom: 2rem;">
    <h1 style="margin: 0 0 0.5rem 0; color: #1f2937; font-size: 2.25rem;">Legal Disclaimers</h1>
    <p style="margin: 0; color: #6b7280; font-size: 1.125rem;">Civics Stack - Court-Defensible Documentation</p>
  </header>
  
  ${metadata}
  
  <main>
    ${disclaimerSections}
  </main>
  
  <footer style="margin-top: 3rem; padding-top: 2rem; border-top: 2px solid #e5e7eb; text-align: center; color: #6b7280; font-size: 0.875rem;">
    <p>This document was generated from the Civics Stack application for documentation and compliance purposes.</p>
    <p>For questions or concerns, please consult with a licensed attorney in your jurisdiction.</p>
  </footer>
</body>
</html>
  `.trim()
}

function generateHTMLForPDF(
  data: DisclaimerExportData,
  options: DisclaimerExportOptions
): string {
  return generateHTMLDocument(data, options)
}

function generateMarkdownDocument(
  data: DisclaimerExportData,
  options: DisclaimerExportOptions
): string {
  let markdown = `# Legal Disclaimers\n## Civics Stack - Court-Defensible Documentation\n\n`

  if (options.includeMetadata) {
    markdown += `### Document Information\n\n`
    markdown += `- **Exported:** ${new Date(data.exportedAt).toLocaleString()}\n`
    if (data.exportedBy) {
      markdown += `- **Exported by:** ${data.exportedBy}\n`
    }
    markdown += `- **Version:** ${data.version}\n`
    markdown += `- **Purpose:** ${data.purpose}\n\n`
    markdown += `---\n\n`
  }

  data.disclaimers.forEach((disclaimer, index) => {
    markdown += `## ${index + 1}. ${disclaimer.title}\n\n`
    markdown += `**ID:** ${disclaimer.id} | **Type:** ${disclaimer.type} | **Version:** ${disclaimer.version} | **Effective:** ${disclaimer.effectiveDate}\n\n`
    markdown += `> ${disclaimer.content.split('\n').join('\n> ')}\n\n`
    markdown += `---\n\n`
  })

  markdown += `### Footer\n\n`
  markdown += `This document was generated from the Civics Stack application for documentation and compliance purposes.\n`
  markdown += `For questions or concerns, please consult with a licensed attorney in your jurisdiction.\n`

  return markdown
}

function generateTextDocument(
  data: DisclaimerExportData,
  options: DisclaimerExportOptions
): string {
  let text = `LEGAL DISCLAIMERS\n`
  text += `Civics Stack - Court-Defensible Documentation\n`
  text += `${'='.repeat(80)}\n\n`

  if (options.includeMetadata) {
    text += `DOCUMENT INFORMATION\n`
    text += `${'-'.repeat(80)}\n`
    text += `Exported: ${new Date(data.exportedAt).toLocaleString()}\n`
    if (data.exportedBy) {
      text += `Exported by: ${data.exportedBy}\n`
    }
    text += `Version: ${data.version}\n`
    text += `Purpose: ${data.purpose}\n\n`
  }

  data.disclaimers.forEach((disclaimer, index) => {
    text += `${'-'.repeat(80)}\n`
    text += `${index + 1}. ${disclaimer.title.toUpperCase()}\n`
    text += `${'-'.repeat(80)}\n`
    text += `ID: ${disclaimer.id}\n`
    text += `Type: ${disclaimer.type}\n`
    text += `Version: ${disclaimer.version}\n`
    text += `Effective Date: ${disclaimer.effectiveDate}\n\n`
    text += `${disclaimer.content}\n\n`
  })

  text += `${'='.repeat(80)}\n`
  text += `FOOTER\n`
  text += `${'-'.repeat(80)}\n`
  text += `This document was generated from the Civics Stack application for\n`
  text += `documentation and compliance purposes. For questions or concerns,\n`
  text += `please consult with a licensed attorney in your jurisdiction.\n`

  return text
}

export function downloadDisclaimer(content: string, format: string, filename?: string) {
  const timestamp = new Date().toISOString().split('T')[0]
  const defaultFilename = `civics-stack-disclaimers-${timestamp}`
  const finalFilename = filename || defaultFilename

  const mimeTypes = {
    html: 'text/html',
    markdown: 'text/markdown',
    text: 'text/plain',
    pdf: 'text/html',
  }

  const extensions = {
    html: 'html',
    markdown: 'md',
    text: 'txt',
    pdf: 'html',
  }

  const blob = new Blob([content], { type: mimeTypes[format as keyof typeof mimeTypes] })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${finalFilename}.${extensions[format as keyof typeof extensions]}`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export function printDisclaimer(content: string) {
  const printWindow = window.open('', '_blank')
  if (printWindow) {
    printWindow.document.write(content)
    printWindow.document.close()
    printWindow.focus()
    setTimeout(() => {
      printWindow.print()
    }, 250)
  }
}

export function copyToClipboard(content: string): Promise<void> {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    return navigator.clipboard.writeText(content)
  }
  
  const textArea = document.createElement('textarea')
  textArea.value = content
  textArea.style.position = 'fixed'
  textArea.style.left = '-999999px'
  document.body.appendChild(textArea)
  textArea.select()
  
  try {
    document.execCommand('copy')
    document.body.removeChild(textArea)
    return Promise.resolve()
  } catch (err) {
    document.body.removeChild(textArea)
    return Promise.reject(err)
  }
}

export function getAllDisclaimerTypes(): DisclaimerType[] {
  return [
    'not-legal-advice',
    'educational-only',
    'no-attorney-client',
    'verify-sources',
    'court-defensibility',
    'accuracy-limitation',
  ]
}
