import { SourceRegistryEntry, VersionSnapshot, ProvenancePanel } from './types'
import { getSourceForDocument } from './source-registry-data'

export interface ProvenanceData {
  sourceRegistry: SourceRegistryEntry[]
  versionSnapshots: VersionSnapshot[]
}

export async function getProvenanceForDocument(documentId: string): Promise<ProvenancePanel | null> {
  // First try document-specific provenance key
  const provenanceKey = `provenance:${documentId}`
  const data = await window.spark.kv.get<ProvenanceData>(provenanceKey)
  
  if (data && data.sourceRegistry && data.sourceRegistry.length > 0) {
    const primarySource = data.sourceRegistry[0]
    const latestVersion = data.versionSnapshots?.[0]

    return {
      sourceRegistryEntry: primarySource,
      versionSnapshot: latestVersion,
      retrievalMetadata: {
        retrievedAt: primarySource.retrievedAt,
        sourceUrl: primarySource.officialUrl,
        checksum: primarySource.checksum || 'N/A',
        parsingMethod: primarySource.retrievalMethod
      },
      verificationChain: [{
        verifiedBy: 'System',
        verifiedAt: primarySource.retrievedAt,
        method: primarySource.retrievalMethod,
        notes: primarySource.curatorJustification || 'Initial verification'
      }]
    }
  }

  // Fall back to the pre-populated source registry
  const registryEntry = getSourceForDocument(documentId)
  if (registryEntry) {
    return {
      sourceRegistryEntry: registryEntry,
      versionSnapshot: undefined,
      retrievalMetadata: {
        retrievedAt: registryEntry.retrievedAt,
        sourceUrl: registryEntry.officialUrl,
        checksum: registryEntry.checksum || 'N/A',
        parsingMethod: registryEntry.retrievalMethod,
      },
      verificationChain: [{
        verifiedBy: 'Curator',
        verifiedAt: registryEntry.lastVerified || registryEntry.retrievedAt,
        method: registryEntry.retrievalMethod,
        notes: registryEntry.curatorJustification || 'Curated from official source',
      }],
    }
  }

  return null
}

export async function createSourceRegistryEntry(
  entry: Omit<SourceRegistryEntry, 'id' | 'retrievedAt'>
): Promise<SourceRegistryEntry> {
  const id = `source-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  const fullEntry: SourceRegistryEntry = {
    ...entry,
    id,
    retrievedAt: new Date().toISOString()
  }

  const allEntries = await window.spark.kv.get<SourceRegistryEntry[]>('source-registry') || []
  await window.spark.kv.set('source-registry', [...allEntries, fullEntry])

  return fullEntry
}

export async function createVersionSnapshot(
  snapshot: Omit<VersionSnapshot, 'id' | 'createdAt'>
): Promise<VersionSnapshot> {
  const id = `version-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  const fullSnapshot: VersionSnapshot = {
    ...snapshot,
    id,
    createdAt: new Date().toISOString()
  }

  const snapshotKey = `versions:${snapshot.documentId}`
  const snapshots = await window.spark.kv.get<VersionSnapshot[]>(snapshotKey) || []
  await window.spark.kv.set(snapshotKey, [fullSnapshot, ...snapshots])

  return fullSnapshot
}

export function generateChecksum(content: string): string {
  let hash = 0
  for (let i = 0; i < content.length; i++) {
    const char = content.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash
  }
  return Math.abs(hash).toString(16).padStart(8, '0')
}

export async function getVersionHistory(documentId: string): Promise<VersionSnapshot[]> {
  const snapshotKey = `versions:${documentId}`
  return await window.spark.kv.get<VersionSnapshot[]>(snapshotKey) || []
}

export async function getSourceRegistry(): Promise<SourceRegistryEntry[]> {
  return await window.spark.kv.get<SourceRegistryEntry[]>('source-registry') || []
}

export function isStaleSource(lastChecked: string, threshold: number = 90): boolean {
  const lastCheckedDate = new Date(lastChecked)
  const today = new Date()
  const daysDiff = Math.floor((today.getTime() - lastCheckedDate.getTime()) / (1000 * 60 * 60 * 24))
  return daysDiff > threshold
}

export function formatProvenanceReport(provenance: ProvenancePanel): string {
  const { sourceRegistryEntry, retrievalMetadata, verificationChain } = provenance
  
  let report = '# Provenance Report\n\n'
  report += `## Source Information\n`
  report += `- **Official URL**: ${sourceRegistryEntry.officialUrl}\n`
  report += `- **Publisher**: ${sourceRegistryEntry.publisher}\n`
  report += `- **Source Type**: ${sourceRegistryEntry.isOfficialSource ? 'Official Government Source' : 'Non-official Mirror'}\n`
  report += `- **Retrieval Method**: ${sourceRegistryEntry.retrievalMethod}\n\n`
  
  report += `## Verification Metadata\n`
  report += `- **Retrieved At**: ${new Date(retrievalMetadata.retrievedAt).toLocaleString()}\n`
  report += `- **Checksum**: ${retrievalMetadata.checksum}\n`
  report += `- **Parsing Method**: ${retrievalMetadata.parsingMethod}\n\n`
  
  if (verificationChain.length > 0) {
    report += `## Verification Chain\n`
    verificationChain.forEach((step, index) => {
      report += `### Verification ${index + 1}\n`
      report += `- **Verified By**: ${step.verifiedBy}\n`
      report += `- **Verified At**: ${new Date(step.verifiedAt).toLocaleString()}\n`
      report += `- **Method**: ${step.method}\n`
      report += `- **Notes**: ${step.notes}\n\n`
    })
  }
  
  report += `\n---\n`
  report += `*This provenance report documents the source, retrieval, and verification of legal content for court-defensible usage.*\n`
  
  return report
}
