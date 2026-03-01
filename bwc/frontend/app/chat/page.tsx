'use client';

import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import {
  chatAsk,
  chatHistory,
  listCases,
  listProjects,
  listEvidence,
  listArtifacts,
  legalSearch,
  type ChatMessage,
  type ChatResponse,
  type ChatCitation,
  type Case,
  type Project,
  type LegalOpinion,
} from '@/lib/api';
import {
  Button,
  Select,
  Badge,
  Card,
  CardContent,
  EmptyState,
  type SelectOption,
} from '@/components/ui';
import { CitationDrawer, type CitationItem } from '@/components/chat/citation-drawer';
import { ResourceLibrary, type ResourceItem } from '@/components/chat/resource-library';

// ── Citation badge (opens drawer on click) ───────────────────────

function CitationBadge({
  citation,
  onClick,
}: {
  citation: ChatCitation;
  onClick: (c: CitationItem) => void;
}) {
  const label =
    citation.source_type === 'courtlistener'
      ? `${citation.court || 'Court'} — ${citation.title || 'Opinion'}`
      : citation.source_type === 'evidence_artifact'
        ? `Artifact: ${citation.title || citation.source_id}`
        : citation.title || citation.source_type;

  function handleClick(e: React.MouseEvent) {
    e.preventDefault();
    onClick({
      id: citation.source_id ?? `cite-${Date.now()}`,
      sourceType: citation.source_type as CitationItem['sourceType'],
      title: label,
      subtitle: citation.court ?? undefined,
      url: citation.url ?? undefined,
      verificationStatus: citation.verification_status,
      snippet: undefined,
    });
  }

  return (
    <button
      onClick={handleClick}
      className="inline-flex items-center gap-1 bg-slate-700/60 border border-slate-600 rounded px-2 py-0.5
                 text-xs text-blue-300 hover:text-blue-200 hover:border-blue-500 transition-colors cursor-pointer"
    >
      <span className="opacity-60">[{citation.verification_status}]</span>
      <span className="truncate max-w-[200px]">{label}</span>
    </button>
  );
}

// ── Message bubble ───────────────────────────────────────────────

function MessageBubble({
  msg,
  onCitationClick,
}: {
  msg: ChatMessage;
  onCitationClick: (c: CitationItem) => void;
}) {
  const isUser = msg.role === 'user';
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-3 ${
          isUser
            ? 'bg-blue-600/80 text-white'
            : 'bg-slate-800 border border-slate-700 text-slate-200'
        }`}
      >
        <p className="whitespace-pre-wrap text-sm">{msg.content}</p>
        {msg.citations && msg.citations.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-2 pt-2 border-t border-slate-600/50">
            {msg.citations.map((c, i) => (
              <CitationBadge key={i} citation={c} onClick={onCitationClick} />
            ))}
          </div>
        )}
        <span className="block text-right text-[10px] mt-1 opacity-40">
          {new Date(msg.created_at).toLocaleTimeString()}
        </span>
      </div>
    </div>
  );
}

// ── Main chat page ───────────────────────────────────────────────

export default function ChatPage() {
  // Scope controls
  const [scope, setScope] = useState<'global' | 'project' | 'case'>('global');
  const [selectedCaseId, setSelectedCaseId] = useState('');
  const [selectedProjectId, setSelectedProjectId] = useState('');

  // Mode: chat vs legal-search
  const [mode, setMode] = useState<'chat' | 'legal'>('chat');

  // Legal search state
  const [legalQuery, setLegalQuery] = useState('');
  const [legalResults, setLegalResults] = useState<LegalOpinion[]>([]);
  const [legalSearching, setLegalSearching] = useState(false);
  const [legalJurisdiction, setLegalJurisdiction] = useState('');

  // Data
  const [cases, setCases] = useState<Case[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  // Input
  const [question, setQuestion] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Citation drawer state
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedCitation, setSelectedCitation] = useState<CitationItem | null>(null);

  // Resource library state
  const [resourcePanelOpen, setResourcePanelOpen] = useState(false);
  const [resources, setResources] = useState<ResourceItem[]>([]);
  const [resourcesLoading, setResourcesLoading] = useState(false);
  const [attachedIds, setAttachedIds] = useState<Set<string>>(new Set());

  const scrollRef = useRef<HTMLDivElement>(null);

  // Open citation drawer
  const handleCitationClick = useCallback((c: CitationItem) => {
    setSelectedCitation(c);
    setDrawerOpen(true);
  }, []);

  // Toggle resource attachment
  const handleAttachResource = useCallback((item: ResourceItem) => {
    setAttachedIds((prev) => {
      const next = new Set(prev);
      if (next.has(item.id)) {
        next.delete(item.id);
      } else {
        next.add(item.id);
      }
      return next;
    });
  }, []);

  // Attached resources for context display
  const attachedResources = useMemo(
    () => resources.filter((r) => attachedIds.has(r.id)),
    [resources, attachedIds]
  );

  // Load projects + cases for scope selectors
  useEffect(() => {
    listCases()
      .then(setCases)
      .catch(() => {});
    listProjects()
      .then(setProjects)
      .catch(() => {});
  }, []);

  // Load chat history when scope changes
  const loadHistory = useCallback(async () => {
    try {
      const caseId = scope === 'case' ? selectedCaseId || undefined : undefined;
      const projectId = scope === 'project' ? selectedProjectId || undefined : undefined;
      const history = await chatHistory(scope, caseId, projectId, 100);
      setMessages(history);
    } catch {
      // silent — history may not exist yet
    }
  }, [scope, selectedCaseId, selectedProjectId]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  // Load resources when case scope changes
  useEffect(() => {
    if (scope !== 'case' || !selectedCaseId) {
      setResources([]);
      return;
    }
    setResourcesLoading(true);
    Promise.all([
      listEvidence(selectedCaseId).catch(() => []),
      listArtifacts(selectedCaseId).catch(() => []),
    ]).then(([evidence, artifacts]) => {
      const items: ResourceItem[] = [
        ...evidence.map((e: any) => ({
          id: e.id,
          type: 'evidence' as const,
          name: e.original_filename || e.id,
          description: e.mime_type,
          status: e.integrity_status ?? undefined,
          sha256: e.sha256 ?? undefined,
          createdAt: e.uploaded_at ?? undefined,
        })),
        ...artifacts.map((a: any) => ({
          id: a.id,
          type: 'artifact' as const,
          name: a.filename || a.id,
          description: a.artifact_type,
          status: a.integrity_status ?? undefined,
          sha256: a.sha256 ?? undefined,
          createdAt: a.created_at ?? undefined,
        })),
      ];
      setResources(items);
      setResourcesLoading(false);
    });
  }, [scope, selectedCaseId]);

  // Auto-scroll to bottom
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  async function handleSend(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim() || sending) return;

    setSending(true);
    setError(null);

    // Optimistic user message
    const userMsg: ChatMessage = {
      id: `temp-${Date.now()}`,
      scope,
      project_id: scope === 'project' ? selectedProjectId : null,
      case_id: scope === 'case' ? selectedCaseId : null,
      role: 'user',
      content: question,
      citations: null,
      verification_status: null,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setQuestion('');

    try {
      const caseId = scope === 'case' ? selectedCaseId || undefined : undefined;
      const projectId = scope === 'project' ? selectedProjectId || undefined : undefined;
      const response: ChatResponse = await chatAsk(question, scope, caseId, projectId);

      // Add assistant response
      const assistantMsg: ChatMessage = {
        id: response.message_id,
        scope,
        project_id: projectId || null,
        case_id: caseId || null,
        role: 'assistant',
        content: response.answer,
        citations: response.citations,
        verification_status: response.verification_status,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get response');
    } finally {
      setSending(false);
    }
  }

  // Legal search handler
  async function handleLegalSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!legalQuery.trim() || legalSearching) return;
    setLegalSearching(true);
    try {
      const results = await legalSearch(legalQuery, {
        jurisdiction: legalJurisdiction || undefined,
      });
      setLegalResults(results);
    } catch {
      setLegalResults([]);
    } finally {
      setLegalSearching(false);
    }
  }

  // Insert legal citation into chat
  function insertCitation(opinion: LegalOpinion) {
    setMode('chat');
    setQuestion(`Regarding ${opinion.case_name} (${opinion.court}, ${opinion.date_filed}):\n`);
  }

  return (
    <div className="flex flex-col h-[calc(100vh-120px)]">
      {/* ── Header + scope controls ──────────────────── */}
      <div className="flex items-center gap-4 mb-4 flex-wrap">
        <h1 className="text-2xl font-bold">Chat</h1>

        {/* Mode switch */}
        <div className="flex gap-1 bg-slate-800 rounded-lg p-0.5 border border-slate-700">
          <Button
            variant={mode === 'chat' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => setMode('chat')}
            data-testid="chat-mode-evidence-btn"
          >
            Evidence QA
          </Button>
          <Button
            variant={mode === 'legal' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => setMode('legal')}
            data-testid="chat-mode-legal-btn"
          >
            Legal Research
          </Button>
        </div>

        {/* Resource panel toggle — visible only when case scoped */}
        {scope === 'case' && selectedCaseId && mode === 'chat' && (
          <Button
            variant={resourcePanelOpen ? 'secondary' : 'ghost'}
            size="sm"
            onClick={() => setResourcePanelOpen((v) => !v)}
            aria-label={resourcePanelOpen ? 'Hide resources' : 'Show resources'}
            data-testid="chat-resources-btn"
          >
            📎 Resources{attachedIds.size > 0 ? ` (${attachedIds.size})` : ''}
          </Button>
        )}

        <div className="flex gap-2 ml-auto">
          {/* Scope tabs */}
          {(['global', 'project', 'case'] as const).map((s) => (
            <Button
              key={s}
              variant={scope === s ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setScope(s)}
              data-testid={`chat-scope-${s}-btn`}
            >
              {s.charAt(0).toUpperCase() + s.slice(1)}
            </Button>
          ))}
        </div>
      </div>

      {/* Scope selectors */}
      {scope === 'project' && (
        <div className="mb-3 max-w-xs" data-testid="chat-scope-section">
          <Select
            label="Project"
            hideLabel
            options={projects.map((p) => ({ value: p.id, label: p.name }))}
            value={selectedProjectId}
            onChange={(e) => setSelectedProjectId(e.target.value)}
            placeholder="Select a project..."
          />
        </div>
      )}
      {scope === 'case' && (
        <div className="mb-3 max-w-xs" data-testid="chat-scope-section">
          <Select
            label="Case"
            hideLabel
            options={cases.map((c) => ({ value: c.id, label: c.title }))}
            value={selectedCaseId}
            onChange={(e) => setSelectedCaseId(e.target.value)}
            placeholder="Select a case..."
          />
        </div>
      )}

      {/* ── Main content area (resource panel + messages) ── */}
      {mode === 'chat' && (
        <div className="flex flex-1 gap-0 overflow-hidden">
          {/* Resource library sidebar */}
          {resourcePanelOpen && scope === 'case' && selectedCaseId && (
            <div
              className="w-72 flex-shrink-0 rounded-l-lg overflow-hidden border border-r-0 border-slate-700"
              data-testid="chat-resource-panel"
            >
              <ResourceLibrary
                items={resources}
                loading={resourcesLoading}
                onAttach={handleAttachResource}
                attachedIds={attachedIds}
              />
            </div>
          )}

          {/* Chat column */}
          <div className="flex-1 flex flex-col min-w-0">
            {/* Attached resources indicator */}
            {attachedResources.length > 0 && (
              <div className="flex flex-wrap gap-1 px-3 py-1.5 bg-slate-800/50 border border-slate-700 rounded-t-lg border-b-0">
                <span className="text-[11px] text-slate-400 mr-1">Context:</span>
                {attachedResources.map((r) => (
                  <Badge key={r.id} variant="info">
                    {r.name}
                    <button
                      onClick={() => handleAttachResource(r)}
                      className="ml-1 opacity-60 hover:opacity-100"
                      aria-label={`Remove ${r.name}`}
                    >
                      ×
                    </button>
                  </Badge>
                ))}
              </div>
            )}

            {/* Messages */}
            <div
              ref={scrollRef}
              className="flex-1 overflow-y-auto bg-slate-900/50 rounded-lg border border-slate-700 p-4 space-y-4"
              data-testid="chat-messages"
            >
              {messages.length === 0 && (
                <div className="flex items-center justify-center h-full text-slate-500">
                  <div className="text-center">
                    <p className="text-lg mb-2">No messages yet</p>
                    <p className="text-sm">
                      Ask about evidence, case law, or procedures. All answers are grounded in your
                      case data and cited legal sources.
                    </p>
                  </div>
                </div>
              )}
              {messages.map((msg) => (
                <MessageBubble key={msg.id} msg={msg} onCitationClick={handleCitationClick} />
              ))}
              {sending && (
                <div className="flex justify-start">
                  <div className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3">
                    <span className="text-slate-400 text-sm animate-pulse">Thinking...</span>
                  </div>
                </div>
              )}
            </div>

            {/* Error */}
            {error && (
              <div className="mt-2 bg-red-900/50 border border-red-600/30 rounded-lg p-2">
                <p className="text-red-200 text-sm">{error}</p>
              </div>
            )}

            {/* ── Input bar ──────────────────────────── */}
            <form onSubmit={handleSend} className="mt-3 flex gap-2">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder={
                  scope === 'case'
                    ? 'Ask about this case...'
                    : scope === 'project'
                      ? 'Ask about this project...'
                      : 'Ask a question...'
                }
                disabled={sending}
                data-testid="chat-message-input"
                className="flex-1 bg-slate-800 border border-slate-600 rounded-lg px-4 py-3
                           text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                           disabled:opacity-50"
              />
              <Button
                type="submit"
                disabled={sending || !question.trim()}
                loading={sending}
                data-testid="chat-send-btn"
              >
                Send
              </Button>
            </form>
          </div>
        </div>
      )}

      {/* ── Legal search mode ────────────────────────── */}
      {mode === 'legal' && (
        <div className="flex-1 flex flex-col overflow-hidden" data-testid="chat-legal-section">
          <form onSubmit={handleLegalSearch} className="flex gap-2 mb-4">
            <input
              type="text"
              value={legalQuery}
              onChange={(e) => setLegalQuery(e.target.value)}
              placeholder="Search case law, e.g. 'excessive force body camera'"
              data-testid="chat-legal-search-input"
              className="flex-1 bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
            <input
              type="text"
              value={legalJurisdiction}
              onChange={(e) => setLegalJurisdiction(e.target.value)}
              placeholder="Jurisdiction (optional)"
              className="w-40 bg-slate-800 border border-slate-600 rounded-lg px-3 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
            <Button
              type="submit"
              disabled={legalSearching || !legalQuery.trim()}
              loading={legalSearching}
              data-testid="chat-legal-search-btn"
            >
              Search
            </Button>
          </form>

          <div className="flex-1 overflow-y-auto space-y-3" data-testid="chat-legal-results">
            {legalResults.length === 0 && !legalSearching && (
              <div className="flex items-center justify-center h-full text-slate-500">
                <div className="text-center">
                  <p className="text-lg mb-2">CourtListener Legal Search</p>
                  <p className="text-sm">
                    Search federal and state case law. Results can be cited in your case issues.
                  </p>
                  <p className="text-xs mt-2 text-slate-600">
                    Powered by CourtListener / Free Law Project
                  </p>
                </div>
              </div>
            )}
            {legalSearching && (
              <div className="text-center py-8">
                <span className="text-slate-400 animate-pulse">Searching CourtListener...</span>
              </div>
            )}
            {legalResults.map((op, i) => (
              <div
                key={i}
                className="bg-slate-800 rounded-lg p-4 border border-slate-700 hover:border-purple-600/50 transition-colors"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-sm text-purple-300">{op.case_name}</h3>
                    <div className="flex gap-3 text-xs text-slate-400 mt-1">
                      <span>{op.court}</span>
                      <span>{op.date_filed}</span>
                      {(op.citation_count ?? 0) > 0 && <span>{op.citation_count} citations</span>}
                    </div>
                    {op.snippet && (
                      <p className="text-xs text-slate-400 mt-2 line-clamp-3">{op.snippet}</p>
                    )}
                  </div>
                  <div className="flex gap-1 flex-shrink-0">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => insertCitation(op)}
                      data-testid="chat-legal-use-in-chat-btn"
                    >
                      Use in Chat
                    </Button>
                    {op.absolute_url && (
                      <a href={op.absolute_url} target="_blank" rel="noopener noreferrer">
                        <Button variant="secondary" size="sm">
                          View
                        </Button>
                      </a>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Citation drawer overlay ──────────────────── */}
      <CitationDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        citation={selectedCitation}
      />
    </div>
  );
}
