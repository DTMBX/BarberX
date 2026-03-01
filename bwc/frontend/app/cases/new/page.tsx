'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { createCase } from '@/lib/api';
import { useToast, Button, Input, PageHeader, Card, CardContent } from '@/components/ui';

export default function NewCasePage() {
  const router = useRouter();
  const { addToast } = useToast();
  const [title, setTitle] = useState('');
  const [createdBy, setCreatedBy] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const newCase = await createCase(title, createdBy || 'default-user');
      addToast('success', `Case "${title}" created`);
      router.push(`/cases/${newCase.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create case');
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-xl">
      <PageHeader
        title="Create New Case"
        breadcrumbs={[{ label: 'Cases', href: '/cases' }, { label: 'New Case' }]}
      />
      <Card className="mt-6">
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6" data-testid="new-case-form">
            {error && (
              <div
                className="rounded-lg border border-red-600/30 bg-red-900/20 p-4"
                data-testid="new-case-error"
              >
                <p className="text-sm text-red-300">{error}</p>
              </div>
            )}
            <Input
              label="Case Title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              placeholder="e.g., BWC-2026-001 Traffic Stop"
              data-testid="new-case-title-input"
            />
            <Input
              label="Created By"
              value={createdBy}
              onChange={(e) => setCreatedBy(e.target.value)}
              placeholder="Your name or ID"
              helperText="Defaults to 'default-user' if left blank"
              data-testid="new-case-created-by-input"
            />
            <div className="flex gap-3">
              <Button
                type="submit"
                loading={submitting}
                disabled={!title}
                data-testid="new-case-submit-btn"
              >
                Create Case
              </Button>
              <Button
                variant="secondary"
                type="button"
                onClick={() => router.back()}
                data-testid="new-case-cancel-btn"
              >
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
