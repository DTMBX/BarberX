import { useEffect, useRef } from 'react'
import type { ImageCardTemplate } from '@/lib/types'

interface VerseImageCardProps {
  verseText: string
  reference: string
  translation: string
  template: ImageCardTemplate
}

export default function VerseImageCard({
  verseText,
  reference,
  translation,
  template
}: VerseImageCardProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const width = 1200
    const height = 630
    canvas.width = width
    canvas.height = height

    ctx.clearRect(0, 0, width, height)

    switch (template) {
      case 'classic':
        drawClassicTemplate(ctx, width, height, verseText, reference, translation)
        break
      case 'modern':
        drawModernTemplate(ctx, width, height, verseText, reference, translation)
        break
      case 'minimalist':
        drawMinimalistTemplate(ctx, width, height, verseText, reference, translation)
        break
      case 'illuminated':
        drawIlluminatedTemplate(ctx, width, height, verseText, reference, translation)
        break
    }
  }, [verseText, reference, translation, template])

  return (
    <canvas
      ref={canvasRef}
      id="verse-card-canvas"
      className="w-full h-auto border rounded-md"
      style={{ aspectRatio: '1200/630' }}
    />
  )
}

function drawClassicTemplate(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  verseText: string,
  reference: string,
  translation: string
) {
  const gradient = ctx.createLinearGradient(0, 0, width, height)
  gradient.addColorStop(0, '#f5f1ea')
  gradient.addColorStop(1, '#e8dfc8')
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, width, height)

  ctx.strokeStyle = 'oklch(0.35 0.08 40)'
  ctx.lineWidth = 8
  ctx.strokeRect(40, 40, width - 80, height - 80)

  ctx.strokeStyle = 'oklch(0.65 0.15 65)'
  ctx.lineWidth = 2
  ctx.strokeRect(60, 60, width - 120, height - 120)

  ctx.fillStyle = 'oklch(0.25 0.02 40)'
  ctx.font = 'italic 48px Georgia, serif'
  ctx.textAlign = 'center'
  const lines = wrapText(ctx, `"${verseText}"`, width - 200)
  const lineHeight = 64
  const startY = (height - lines.length * lineHeight) / 2
  lines.forEach((line, i) => {
    ctx.fillText(line, width / 2, startY + i * lineHeight)
  })

  ctx.font = '32px Georgia, serif'
  ctx.fillStyle = 'oklch(0.45 0.06 30)'
  ctx.fillText(`— ${reference}`, width / 2, height - 120)

  ctx.font = '24px Georgia, serif'
  ctx.fillStyle = 'oklch(0.556 0 0)'
  ctx.fillText(translation.toUpperCase(), width / 2, height - 80)
}

function drawModernTemplate(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  verseText: string,
  reference: string,
  translation: string
) {
  ctx.fillStyle = 'oklch(0.25 0.02 40)'
  ctx.fillRect(0, 0, width, height)

  ctx.fillStyle = 'oklch(0.65 0.15 65)'
  ctx.fillRect(0, 0, 20, height)

  ctx.fillStyle = 'oklch(0.99 0 0)'
  ctx.font = 'bold 52px sans-serif'
  ctx.textAlign = 'left'
  const lines = wrapText(ctx, verseText, width - 200)
  const lineHeight = 72
  const startY = 150
  lines.forEach((line, i) => {
    ctx.fillText(line, 100, startY + i * lineHeight)
  })

  ctx.font = 'bold 36px sans-serif'
  ctx.fillStyle = 'oklch(0.65 0.15 65)'
  ctx.fillText(reference, 100, height - 120)

  ctx.font = '28px sans-serif'
  ctx.fillStyle = 'oklch(0.708 0 0)'
  ctx.fillText(translation.toUpperCase(), 100, height - 70)
}

function drawMinimalistTemplate(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  verseText: string,
  reference: string,
  translation: string
) {
  ctx.fillStyle = 'oklch(0.99 0 0)'
  ctx.fillRect(0, 0, width, height)

  ctx.fillStyle = 'oklch(0.25 0.02 40)'
  ctx.font = '44px serif'
  ctx.textAlign = 'center'
  const lines = wrapText(ctx, verseText, width - 300)
  const lineHeight = 64
  const startY = (height - lines.length * lineHeight) / 2
  lines.forEach((line, i) => {
    ctx.fillText(line, width / 2, startY + i * lineHeight)
  })

  ctx.fillStyle = 'oklch(0.556 0 0)'
  ctx.fillRect((width - 100) / 2, height / 2 + 100, 100, 2)

  ctx.font = '28px serif'
  ctx.fillStyle = 'oklch(0.45 0.02 40)'
  ctx.fillText(reference, width / 2, height - 100)

  ctx.font = '20px serif'
  ctx.fillStyle = 'oklch(0.556 0 0)'
  ctx.fillText(translation.toUpperCase(), width / 2, height - 60)
}

function drawIlluminatedTemplate(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  verseText: string,
  reference: string,
  translation: string
) {
  const gradient = ctx.createRadialGradient(width / 2, height / 2, 0, width / 2, height / 2, width / 2)
  gradient.addColorStop(0, 'oklch(0.35 0.08 40)')
  gradient.addColorStop(1, 'oklch(0.2 0.06 35)')
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, width, height)

  for (let i = 0; i < 50; i++) {
    ctx.fillStyle = `oklch(0.65 0.15 65 / ${Math.random() * 0.3})`
    ctx.beginPath()
    ctx.arc(Math.random() * width, Math.random() * height, Math.random() * 3, 0, Math.PI * 2)
    ctx.fill()
  }

  ctx.strokeStyle = 'oklch(0.65 0.15 65)'
  ctx.lineWidth = 4
  ctx.strokeRect(80, 80, width - 160, height - 160)

  ctx.fillStyle = 'oklch(0.99 0 0)'
  ctx.font = 'italic 46px Georgia, serif'
  ctx.textAlign = 'center'
  const lines = wrapText(ctx, `"${verseText}"`, width - 240)
  const lineHeight = 64
  const startY = (height - lines.length * lineHeight) / 2
  lines.forEach((line, i) => {
    ctx.fillText(line, width / 2, startY + i * lineHeight)
  })

  ctx.font = 'bold 32px Georgia, serif'
  ctx.fillStyle = 'oklch(0.65 0.15 65)'
  ctx.fillText(reference, width / 2, height - 110)

  ctx.font = '24px Georgia, serif'
  ctx.fillStyle = 'oklch(0.85 0.1 60)'
  ctx.fillText(translation.toUpperCase(), width / 2, height - 70)
}

function wrapText(ctx: CanvasRenderingContext2D, text: string, maxWidth: number): string[] {
  const words = text.split(' ')
  const lines: string[] = []
  let currentLine = ''

  for (const word of words) {
    const testLine = currentLine + (currentLine ? ' ' : '') + word
    const metrics = ctx.measureText(testLine)
    if (metrics.width > maxWidth && currentLine) {
      lines.push(currentLine)
      currentLine = word
    } else {
      currentLine = testLine
    }
  }
  if (currentLine) {
    lines.push(currentLine)
  }

  return lines
}
